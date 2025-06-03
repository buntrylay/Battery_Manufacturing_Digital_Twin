from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from simulation.factory.Factory import Factory
from simulation.battery_model.Slurry import Slurry
from simulation.machine.MixingMachine import MixingMachine
from simulation.machine.CoatingMachine import CoatingMachine
from simulation.machine.DryingMachine import DryingMachine
from simulation.machine.CalendaringMachine import CalendaringMachine
from simulation.machine.SlittingMachine import SlittingMachine
from simulation.machine.ElectrodeInspectionMachine import ElectrodeInspectionMachine
from simulation.machine.RewindingMachine import RewindingMachine
from pathlib import Path
from zipfile import ZipFile
import json
import shutil
from glob import glob
import time
from typing import List
import asyncio
from contextlib import asynccontextmanager

connected_clients: List[WebSocket] = []
event_loop = None  # ✨ Global reference to main event loop

@asynccontextmanager
async def lifespan(app: FastAPI):
    global event_loop
    event_loop = asyncio.get_running_loop()
    print("[WebSocket] Main event loop registered.")
    yield
    # You could clean up here if needed

# Broadcast function to send message to all connected clients
async def broadcast_status(message: str):
    for client in connected_clients:
        try:
            await client.send_text(message)
        except:
            connected_clients.remove(client)

# Thread-safe broadcast from non-async functions (e.g., threads)
def thread_broadcast(message: str):
    global event_loop
    if event_loop and event_loop.is_running():
        future = asyncio.run_coroutine_threadsafe(broadcast_status(message), event_loop)
        try:
            # ✨ Yield control briefly to allow WebSocket flush
            future.result(timeout=0.1)
        except Exception:
            print(f"[WebSocket] Broadcast timeout or error: {message}")
    else:
        print(f"[WebSocket] Skipped broadcast (no event loop): {message}")

app = FastAPI(lifespan=lifespan)

# Allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RESULTS_PATH = Path("results")
RESULTS_PATH.mkdir(parents=True, exist_ok=True)

class SlurryInput(BaseModel):
    PVDF: float
    CA: float
    AM: float
    Solvent: float
    electrode_type: str

class DualInput(BaseModel):
    anode: SlurryInput
    cathode: SlurryInput

factory = Factory()
machines = {}

@app.post("/start-both")
async def start_both_simulation(payload: DualInput):
    return await asyncio.to_thread(_run_simulation, payload)

def _run_simulation(payload: DualInput):
    try:
        thread_broadcast("🔄 Initializing factory and clearing previous simulation...")  # ✨ WebSocket status update
        factory.stop_simulation()
        factory.machines = []
        factory.threads = []
        factory.machine_status = {}
        factory.machine_locks = {}
        factory.machine_events = {}

        for data in [payload.anode, payload.cathode]:
            thread_broadcast(f"🧪 Starting Mixing Stage: {data.electrode_type}")  # ✨ WebSocket status update
            slurry = Slurry(data.electrode_type)
            ratios = {
                "PVDF": data.PVDF,
                "CA": data.CA,
                "AM": data.AM,
                "H2O" if data.electrode_type == "Anode" else "NMP": data.Solvent
            }

            machine_id = f"TK_Mix_{data.electrode_type}"
            mixing_machine = MixingMachine(machine_id, data.electrode_type, slurry, ratios)
            factory.add_machine(mixing_machine)
            machines[data.electrode_type] = mixing_machine
            thread_broadcast(f"✅ Completed Mixing Stage: {data.electrode_type}")  # ✨ WebSocket status update

        thread_broadcast("🧴 Adding Coating Machines...")  # ✨ WebSocket status update
        user_input_coating = {
            "coating_speed": 0.05,
            "gap_height": 200e-6,
            "flow_rate": 5e-6,
            "coating_width": 0.5
        }

        anode_coating_machine = CoatingMachine("MC_Coat_Anode", user_input_coating)
        cathode_coating_machine = CoatingMachine("MC_Coat_Cathode", user_input_coating)

        factory.add_machine(anode_coating_machine, dependencies=["TK_Mix_Anode"])
        factory.add_machine(cathode_coating_machine, dependencies=["TK_Mix_Cathode"])

        machines["Anode_Coating"] = anode_coating_machine
        machines["Cathode_Coating"] = cathode_coating_machine
        thread_broadcast("✅ Coating Machines Added")  # ✨ WebSocket status update

        # Add Drying machines
        thread_broadcast("💨 Adding Drying Machines...")  # ✨ WebSocket status update
        for etype in ["Anode", "Cathode"]:
            drying_id = f"MC_Dry_{etype}"
            coat_id = f"MC_Coat_{etype}"
            drying_machine = DryingMachine(drying_id, web_speed=0.5)
            factory.add_machine(drying_machine, dependencies=[coat_id])
            machines[f"{etype}_Drying"] = drying_machine
        thread_broadcast("✅ Drying Machines Added")  # ✨ WebSocket status update

        # Add Calendaring machines
        thread_broadcast("🧲 Adding Calendaring Machines...")  # ✨ WebSocket status update
        user_input_calendaring = {
            "roll_gap": 100e-6,             # meters
            "roll_pressure": 2e6,           # Pascals
            "roll_speed": 2.0,              # m/s
            "dry_thickness": 150e-6,        # From coating (m)
            "initial_porosity": 0.45,       # Assumed porosity after drying
            "temperature": 25               # Optional
        }
        for etype in ["Anode", "Cathode"]:
            calendaring_id = f"MC_Cal_{etype}"
            drying_id = f"MC_Dry_{etype}"
            calendaring_machine = CalendaringMachine(calendaring_id, user_input_calendaring)
            factory.add_machine(calendaring_machine, dependencies=[drying_id])
            machines[f"{etype}_Calendaring"] = calendaring_machine
        thread_broadcast("✅ Calendaring Machines Added")  # ✨ WebSocket status update

        # Add Slitting machines
        thread_broadcast("🔪 Adding Slitting Machines...")  # ✨ WebSocket status update
        user_input_slitting = {
            "w_input": 500,
            "blade_sharpness": 8,
            "slitting_speed": 1.5, 
            "target_width": 100,
            "slitting_tension": 150,
        }
        for etype in ["Anode", "Cathode"]:
            slitting_id = f"MC_Slit_{etype}"
            calendaring_id = f"MC_Cal_{etype}"
            slitting_machine = SlittingMachine(slitting_id, user_input_slitting)
            factory.add_machine(slitting_machine, dependencies=[calendaring_id])
            machines[f"{etype}_Slitting"] = slitting_machine
        thread_broadcast("✅ Slitting Machines Added")  # ✨ WebSocket status update

        # Add Electrode Inspection machines
        thread_broadcast("🔍 Adding Electrode Inspection Machines...")  # ✨ WebSocket status update
        user_input_electrode_inspection = {
            "epsilon_width_max": 0.1,  
            "epsilon_thickness_max": 10e-6,
            "B_max": 2.0,
            "D_surface_max": 3
        }
        for etype in ["Anode", "Cathode"]:
            inspection_id = f"MC_Inspect_{etype}"
            slitting_id = f"MC_Slit_{etype}"
            inspection_machine = ElectrodeInspectionMachine(inspection_id, user_input_electrode_inspection)
            factory.add_machine(inspection_machine, dependencies=[slitting_id])
            machines[f"{etype}_Inspection"] = inspection_machine
        thread_broadcast("✅ Electrode Inspection Machines Added")  # ✨ WebSocket status update
        
           
        user_input_rewinding = {
            "rewinding_speed": 0.5,  # m/s
            "initial_tension": 100,       # N
            "tapering_steps": 0.3, # meters
            "environment_humidity": 30    # %
        }
        
        for etype in ["Anode", "Cathode"]:
            rewinding_id = f"MC_Rewind_{etype}"
            inspection_id = f"MC_Inspect_{etype}"
            rewinding_machine = RewindingMachine(rewinding_id, user_input_rewinding)
            factory.add_machine(rewinding_machine, dependencies=[inspection_id])
            machines[f"{etype}_Rewinding"] = rewinding_machine

        thread_broadcast("🚀 Starting Full Simulation...")  # ✨ WebSocket status update
        factory.start_simulation()

        for thread in factory.threads:
            thread.join()
        thread_broadcast("✅ Simulation Complete")  # ✨ WebSocket status update

        all_completed = all(factory.machine_status.values())
        if not all_completed:
            thread_broadcast("❌ Some machines failed to complete")  # ✨ WebSocket status update
            raise Exception("Not all machines completed successfully")

        for data in [payload.anode, payload.cathode]:
            machine = machines[data.electrode_type]
            final_result = machine._format_result(is_final=True)
            result_path = RESULTS_PATH / f"{data.electrode_type}_result.json"
            with open(result_path, "w") as f:
                json.dump(final_result, f, indent=4)
            thread_broadcast(f"📁 Results saved for {data.electrode_type}")  # ✨ WebSocket status update

        completion_status = {
            machine_id: {
                "completed": status,
                "timestamp": machines[data.electrode_type]._format_result(is_final=True)["TimeStamp"]
                if machine_id != "Coating_Machine" else "N/A"
            }
            for machine_id, status in factory.machine_status.items()
        }

        thread_broadcast("🎉 All processes completed successfully.")  # ✨ WebSocket status update
        return {
            "message": "All processes completed successfully.",
            "completion_status": completion_status
        }

    except Exception as e:
        thread_broadcast(f"❌ Error: {str(e)}")  # ✨ WebSocket status update
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
def reset_simulation():
    try:
        shutil.rmtree(RESULTS_PATH)
        RESULTS_PATH.mkdir()
        factory.reset()
        machines.clear()
        return {"message": "Factory and data reset."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{electrode_type}")
def download_result_zip(electrode_type: str):
    try:
        zip_path = RESULTS_PATH / f"{electrode_type}.zip"
        with ZipFile(zip_path, "w") as zipf:
            for file in (Path.cwd() / "simulation_output").glob(f"*{electrode_type}*.json"):
                zipf.write(file, arcname=file.name)
        return FileResponse(zip_path, media_type='application/zip', filename=f"{electrode_type}.zip")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# ✨ WebSocket endpoint to accept connections from frontend
@app.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # keep connection alive
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

# (Optional) Download all results as a zip
'''
@app.get("/files/all")
def download_all_results():
    try:
        zip_path = RESULTS_PATH / "all_results.zip"
        json_files = list(RESULTS_PATH.glob("*.json"))
        if not json_files:
            raise FileNotFoundError("No result file for all")
        with ZipFile(zip_path, "w") as zipf:
            for file in json_files:
                zipf.write(file, arcname=file.name)
        return FileResponse(zip_path, media_type='application/zip', filename="all_results.zip")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''