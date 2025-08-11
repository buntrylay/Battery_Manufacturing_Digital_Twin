# server/main.py  — SimPy Mixing POC (keeps your WS + download endpoints)

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from zipfile import ZipFile
from glob import glob
from collections import deque
from datetime import datetime, timedelta
from typing import List
import asyncio
import json
import os
import shutil

# ---- Your existing domain models (unchanged) ----
from simulation.battery_model.Slurry import Slurry
from simulation.sensor.SlurryPropertyCalculator import SlurryPropertyCalculator

# ---- NEW: SimPy for mixing ----
import simpy


# ======================================================================================
# WebSocket infra (unchanged from your current file)
# ======================================================================================

MAX_MESSAGE = 100
message_queue = deque(maxlen=MAX_MESSAGE)
message_lock = asyncio.Lock()  # asyncio-friendly

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # blast to live connections
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
            except Exception:
                # drop dead sockets silently
                try:
                    self.disconnect(connection)
                except Exception:
                    pass

manager = ConnectionManager()

def _timestamped(msg: str) -> str:
    return f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"

# thread-safe-ish broadcaster usable from anywhere
def thread_broadcast(message: str):
    formatted = _timestamped(message)
    try:
        # store to queue for history (no await)
        message_queue.append(formatted)
        # schedule async broadcast
        asyncio.get_event_loop().create_task(manager.broadcast(formatted))
    except RuntimeError:
        # if no running loop (e.g., called from a sync thread), fallback
        try:
            asyncio.run(manager.broadcast(formatted))
        except Exception:
            pass


# ======================================================================================
# FastAPI setup
# ======================================================================================

app = FastAPI()

# Allow frontend communication (your React app)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RESULTS_PATH = Path("results")
RESULTS_PATH.mkdir(parents=True, exist_ok=True)

SIM_OUT = Path.cwd() / "simulation_output"
SIM_OUT.mkdir(parents=True, exist_ok=True)


# ======================================================================================
# Payload models (unchanged)
# ======================================================================================

class SlurryInput(BaseModel):
    PVDF: float
    CA: float
    AM: float
    Solvent: float
    electrode_type: str

class DualInput(BaseModel):
    anode: SlurryInput
    cathode: SlurryInput


# ======================================================================================
# SimPy Mixing implementation (self-contained here)
# ======================================================================================

class MixingSimPy:
    """
    SimPy-only mixer that mimics your MixingMachine behavior closely:
      - Pre-adds solvent
      - Adds PVDF -> CA -> AM gradually (step_percent)
      - Writes snapshots + final JSON into simulation_output/
      - Broadcasts status over your WebSocket
    """

    def __init__(
        self,
        machine_id: str,
        electrode_type: str,
        slurry: Slurry,
        ratios: dict,
        volume_l: float = 200.0,
        step_percent: float = 0.02,  # 2% increments
        tick_sim_s: float = 0.1      # simulated seconds per step
    ):
        self.id = machine_id
        self.electrode_type = electrode_type
        self.slurry = slurry
        self.ratios = ratios
        self.volume = volume_l
        self.step_percent = step_percent
        self.tick = tick_sim_s
        self.start_dt = datetime.now()
        self.env = simpy.Environment()

        # params to mirror your calculator init
        if electrode_type == "Anode":
            self.RHO_values = {"AM": 2.26, "CA": 1.8, "PVDF": 1.17, "H2O": 1.0}
            self.WEIGHTS_values = {"a": 0.85, "b": 2.2, "c": 0.3, "s": -0.4}
            solvent_key = "H2O"
        else:
            self.RHO_values = {"AM": 2.11, "CA": 1.8, "PVDF": 1.78, "NMP": 1.03}
            self.WEIGHTS_values = {"a": 0.9, "b": 2.5, "c": 0.3, "s": -0.5}
            solvent_key = "NMP"

        self.solvent_key = solvent_key
        self.calc = SlurryPropertyCalculator(self.RHO_values, self.WEIGHTS_values)

        # Pre-add solvent (matches your current thread mixer)
        self.slurry.add(solvent_key, self.volume * self.ratios[solvent_key])

        self._last_save_wall = datetime.now()
        self._last_snapshot = None

    # ---------- formatting & saving ----------
    def _format_snapshot(self, sim_t: float, final: bool = False):
        ts = (self.start_dt + timedelta(seconds=sim_t)).isoformat()
        base = {
            "TimeStamp": ts,
            "Duration": round(sim_t, 5),
            "Machine ID": self.id,
            "Process": "Mixing",
            "Electrode Type": self.electrode_type
        }
        composition = {
            "AM": round(getattr(self.slurry, "AM", 0.0), 3),
            "CA": round(getattr(self.slurry, "CA", 0.0), 3),
            "PVDF": round(getattr(self.slurry, "PVDF", 0.0), 3),
            self.solvent_key: round(getattr(self.slurry, self.solvent_key, 0.0), 3),
        }
        properties = {
            "Density": round(self.calc.calculate_density(self.slurry), 4),
            "Viscosity": round(self.calc.calculate_viscosity(self.slurry), 2),
            "YieldStress": round(self.calc.calculate_yield_stress(self.slurry), 2),
        }
        if final:
            base["Final Composition"] = composition
            base["Final Properties"] = properties
        else:
            base.update(composition)
            base.update(properties)
        return base

    def _save_json(self, payload: dict, label: str):
        # filename includes electrode type so your /files/{electrode_type} finds them
        safe_ts = payload["TimeStamp"].replace(":", "-").replace(".", "-")
        fname = f"{self.id}_{self.electrode_type}_{safe_ts}_{label}.json"
        fpath = SIM_OUT / fname
        if not fpath.exists():
            with open(fpath, "w") as f:
                json.dump(payload, f, indent=4)
        return str(fpath)

    # ---------- the SimPy process ----------
    def _mix_component(self, component: str):
        total = self.volume * self.ratios[component]
        step = max(total * self.step_percent, 1e-9)
        added = 0.0
        while added < total:
            yield self.env.timeout(self.tick)
            self.slurry.add(component, min(step, total - added))
            added += step

            # throttle snapshots (every ~100ms wall time)
            now_wall = datetime.now()
            if (now_wall - self._last_save_wall).total_seconds() >= 0.1:
                snap = self._format_snapshot(self.env.now, final=False)
                if snap != self._last_snapshot:
                    self._save_json(snap, f"result_at_{round(self.env.now)}s")
                    self._last_snapshot = snap
                    self._last_save_wall = now_wall
                    thread_broadcast(f"SimPy {self.id} {component} progress @ {round(self.env.now,1)}s")

    def run(self):
        thread_broadcast(f"SimPy {self.id} mixing started.")
        # PVDF -> CA -> AM
        for c in ["PVDF", "CA", "AM"]:
            self.env.process(self._mix_component(c))
            # wait for each component to finish before next (serial)
            self.env.run()  # runs until no events (i.e., component done)

        # final snapshot
        final = self._format_snapshot(self.env.now, final=True)
        final_path = self._save_json(final, "final")
        # push computed props back to slurry (parity)
        props = final.get("Final Properties", {})
        if hasattr(self.slurry, "update_properties"):
            self.slurry.update_properties(
                props.get("Viscosity", 0.0),
                props.get("Density", 0.0),
                props.get("YieldStress", 0.0),
            )
        thread_broadcast(f"SimPy {self.id} mixing completed. -> {os.path.basename(final_path)}")
        return final


# ======================================================================================
# API routes
# ======================================================================================

@app.post("/start-both")
def start_both_simulation(payload: DualInput):
    """
    SimPy-only Mixing for both Anode & Cathode.
    Writes snapshots/finals to simulation_output/ and returns completion info.
    """
    try:
        # Clean previous outputs to avoid confusion
        if SIM_OUT.exists():
            for f in SIM_OUT.glob("*.json"):
                try:
                    f.unlink()
                except Exception:
                    pass

        # run Anode then Cathode (separate mixers)
        results = {}

        for data in [payload.anode, payload.cathode]:
            slurry = Slurry(data.electrode_type)
            solvent_key = "H2O" if data.electrode_type.lower() == "anode" else "NMP"
            ratios = {"PVDF": data.PVDF, "CA": data.CA, "AM": data.AM, solvent_key: data.Solvent}

            machine_id = f"TK_Mix_{data.electrode_type}_SimPy"
            mixer = MixingSimPy(
                machine_id=machine_id,
                electrode_type=data.electrode_type,
                slurry=slurry,
                ratios=ratios,
                volume_l=200.0,
                step_percent=0.02,
                tick_sim_s=0.1
            )
            final_payload = mixer.run()
            results[data.electrode_type] = final_payload

        # Build a simple completion status compatible with your UI
        completion_status = {
            f"TK_Mix_{etype}_SimPy": {
                "completed": True,
                "timestamp": results[etype]["TimeStamp"]
            }
            for etype in results.keys()
        }

        return {
            "message": "Mixing (SimPy) completed for both electrodes.",
            "completion_status": completion_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/reset")
def reset_simulation():
    try:
        # clear results/ and simulation_output/
        if RESULTS_PATH.exists():
            shutil.rmtree(RESULTS_PATH, ignore_errors=True)
        RESULTS_PATH.mkdir(parents=True, exist_ok=True)

        if SIM_OUT.exists():
            for f in SIM_OUT.glob("*.json"):
                try:
                    f.unlink()
                except Exception:
                    pass

        thread_broadcast("✅ Reset completed (results + simulation_output cleared).")
        return {"message": "Reset complete."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/files/{electrode_type}")
def download_result_zip(electrode_type: str):
    """
    Zips all JSONs from simulation_output/ containing {electrode_type} in filename.
    Same behavior as your current endpoint, but targets SimPy mixer outputs.
    """
    try:
        zip_path = RESULTS_PATH / f"{electrode_type}.zip"
        with ZipFile(zip_path, "w") as zipf:
            for file in SIM_OUT.glob(f"*{electrode_type}*.json"):
                zipf.write(file, arcname=file.name)

        if not zip_path.exists() or zip_path.stat().st_size == 0:
            raise FileNotFoundError(f"No files found for {electrode_type}")

        return FileResponse(zip_path, media_type="application/zip", filename=f"{electrode_type}.zip")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


# ======================================================================================
# WebSocket endpoint (unchanged path)
# ======================================================================================

@app.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # send recent history on connect
        for msg in list(message_queue):
            try:
                await websocket.send_text(msg)
            except Exception:
                pass

        while True:
            # keep alive / optionally receive from client
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
