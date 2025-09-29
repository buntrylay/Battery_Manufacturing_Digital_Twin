import os
import time
import threading
from collections import deque
from datetime import datetime
from typing import List, Dict, Any

import sqlalchemy
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio

# Import database engine & session
from backend.src.server.db.db import engine, SessionLocal
from backend.src.server.db.model_table import *
# Import the machine and model classes directly
from simulation.battery_model.MixingModel import MixingModel
from simulation.machine.MixingMachine import MixingMachine
from simulation.battery_model.CoatingModel import CoatingModel
from simulation.machine.CoatingMachine import CoatingMachine
from simulation.process_parameters.Parameters import MixingParameters, CoatingParameters

import uuid

MAX_MESSAGES = 100
message_queue = deque(maxlen=MAX_MESSAGES)
message_lock = threading.Lock()
simulation_lock = threading.Lock()
main_loop = None

### Db writing
MAX_DB_QUEUE_SIZE = 1000
db_queue = deque(maxlen=MAX_DB_QUEUE_SIZE)
db_lock = threading.Lock()
db_worker_thread = None
db_worker_running = False

def thread_queue_db_data(payload: Dict[str, Any]):
    """Thread-safe database queue - adds data to be persisted"""
    with db_lock:
        # Add timestamp if not present
        if 'timestamp' not in payload:
            payload['timestamp'] = datetime.now().isoformat()
        db_queue.append(payload)

def db_worker():
    """Background worker that processes database queue every 5 seconds"""
    global db_worker_running
    db_worker_running = True
    
    while db_worker_running:
        time.sleep(5)  # Process every 5 seconds
        
        if not db_queue:
            continue
            
        # Batch process all queued data
        batch_data = []
        with db_lock:
            while db_queue and len(batch_data) < 50:  # Process up to 50 records at once
                batch_data.append(db_queue.popleft())
        
        if batch_data:
            try:
                db = SessionLocal()
                saved_count = 0
                for data in batch_data:
                    record = create_db_record(data)
                    if record:
                        db.add(record)
                        saved_count += 1
                
                db.commit()
                thread_broadcast(f"✓ Saved {saved_count} records to database")
                
            except Exception as e:
                thread_broadcast(f"✗ Database error: {str(e)}")
                # Could log failed data to file for debugging
                with open("failed_db_writes.log", "a") as f:
                    f.write(f"[{datetime.now()}] Failed to save {len(batch_data)} records: {e}\n")
            finally:
                db.close()

def create_db_record(simulation_data: Dict[str, Any]):
    """Map simulation data to appropriate database table"""

    def safe_float(val, default=0.0):
                try:
                    return float(val)
                except Exception:
                    return default
                
    try:
        process_type = simulation_data.get('process', 'unknown')
        
        if process_type == 'Anode_Mixer':
            battery_model = simulation_data.get('battery_model', {})
            machine_params = simulation_data.get('machine_parameters', {})

            return AnodeMixing(
                batch=simulation_data.get('batch_id', 1),
                state=simulation_data.get('state', 'Unknown'),
                timestamp=datetime.fromisoformat(simulation_data['timestamp']),
                duration=safe_float(simulation_data.get('duration', 0.0)),
                process=simulation_data.get('process', 'mixing_anode'),
                temperature_C=safe_float(simulation_data.get('temperature_C', 0.0)),
                am_volume_L=safe_float(battery_model.get('AM_volume', 0.0)),
                ca_volume_L=safe_float(battery_model.get('CA_volume', 0.0)),
                pvdf_volume_L=safe_float(battery_model.get('PVDF_volume', 0.0)),
                solvent_volume_L=safe_float(battery_model.get('H2O_volume', 0.0)),
                viscosity_Pa_s=safe_float(battery_model.get('viscosity', 0.0)),
                density_kg_m3=safe_float(battery_model.get('density', 0.0)),
                yield_stress_Pa=safe_float(battery_model.get('yield_stress', 0.0)),
                total_volume_L=safe_float(battery_model.get('total_volume', 0.0)),
                am=safe_float(machine_params.get('AM_ratio', 0.0)),
                ca=safe_float(machine_params.get('CA_ratio', 0.0)),
                pvdf=safe_float(machine_params.get('PVDF_ratio', 0.0)),
                solvent=safe_float(machine_params.get('solvent_ratio', 0.0))
            )
        
        elif process_type == 'Cathode_Mixer':
            battery_model = simulation_data.get('battery_model', {})
            machine_params = simulation_data.get('machine_parameters', {})

            return CathodeMixing(
                batch=simulation_data.get('batch_id', 1),
                state=simulation_data.get('state', 'Unknown'),
                timestamp=datetime.fromisoformat(simulation_data['timestamp']),
                duration=safe_float(simulation_data.get('duration', 0.0)),
                process=simulation_data.get('process', 'mixing_anode'),
                temperature_C=safe_float(simulation_data.get('temperature_C', 0.0)),
                am_volume_L=safe_float(battery_model.get('AM_volume', 0.0)),
                ca_volume_L=safe_float(battery_model.get('CA_volume', 0.0)),
                pvdf_volume_L=safe_float(battery_model.get('PVDF_volume', 0.0)),
                solvent_volume_L=safe_float(battery_model.get('H2O_volume', 0.0)),
                viscosity_Pa_s=safe_float(battery_model.get('viscosity', 0.0)),
                density_kg_m3=safe_float(battery_model.get('density', 0.0)),
                yield_stress_Pa=safe_float(battery_model.get('yield_stress', 0.0)),
                total_volume_L=safe_float(battery_model.get('total_volume', 0.0)),
                am=safe_float(machine_params.get('AM_ratio', 0.0)),
                ca=safe_float(machine_params.get('CA_ratio', 0.0)),
                pvdf=safe_float(machine_params.get('PVDF_ratio', 0.0)),
                solvent=safe_float(machine_params.get('solvent_ratio', 0.0))
            )
        
        # Future: Add other process types
        # elif process_type == 'coating_anode':
        #     return AnodeCoating(...)
        
        else:
            thread_broadcast(f"⚠ Unknown process type: {process_type}")
            return None
            
    except Exception as e:
        thread_broadcast(f"✗ Error creating DB record: {str(e)}")
        # Log the problematic data for debugging
        thread_broadcast(f"Problematic data: {simulation_data}")
        return None

def stop_db_worker():
    """Gracefully stop the database worker"""
    global db_worker_running
    db_worker_running = False
    if db_worker_thread:
        db_worker_thread.join(timeout=10)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def _send_message(self, websocket: WebSocket, message: str):
        try:
            await websocket.send_text(message)
        except Exception:
            self.disconnect(websocket)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        with message_lock:
            for msg in message_queue:
                await websocket.send_text(msg)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    def broadcast(self, message: str):
        for connection in self.active_connections:
            asyncio.create_task(self._send_message(connection, message))

manager = ConnectionManager()

# Data (JSON) broadcasting
data_queue = deque(maxlen=MAX_MESSAGES)
data_lock = threading.Lock()

class DataConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def _send_json(self, websocket: WebSocket, payload: Dict[str, Any]):
        try:
            await websocket.send_json(payload)
        except Exception:
            self.disconnect(websocket)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        with data_lock:
            for obj in data_queue:
                await websocket.send_json(obj)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    def broadcast_json(self, payload: Dict[str, Any]):
        for connection in self.active_connections:
            asyncio.create_task(self._send_json(connection, payload))

data_manager = DataConnectionManager()

def thread_broadcast(message: str):
    global main_loop
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    with message_lock:
        message_queue.append(formatted_message)
    if main_loop and main_loop.is_running():
        main_loop.call_soon_threadsafe(manager.broadcast, formatted_message)

def thread_broadcast_data(payload: Dict[str, Any]):
    """Thread-safe JSON data broadcast to /ws/data with small backlog."""
    global main_loop
    with data_lock:
        data_queue.append(payload)
    if main_loop and main_loop.is_running():
        main_loop.call_soon_threadsafe(data_manager.broadcast_json, payload)

class SlurryInput(BaseModel):
    PVDF: float
    CA: float
    AM: float
    Solvent: float

class SimulationInput(BaseModel):
    anode: SlurryInput
    cathode: SlurryInput

def _add_process(results: list, process: str) -> list:
    if not isinstance(results, list):
        return []
    for r in results:
        if isinstance(r, dict):
            r["process"] = process
    return results

# Defaults for coating (tune as needed or make request-driven)
COATING_DEFAULTS = dict(
    coating_speed=1.0,
    gap_height=0.1,
    flow_rate=5.0,
    coating_width=0.5,
)

def run_mixing(electrode_name: str, slurry: SlurryInput):
    thread_broadcast(f"--- Starting {electrode_name} Mixing ---")
    # Generate unique batch ID for this run
    batch_id = str(uuid.uuid4())
    
    params = MixingParameters(
        AM_ratio=slurry.AM,
        CA_ratio=slurry.CA,
        PVDF_ratio=slurry.PVDF,
        solvent_ratio=slurry.Solvent,
    )
    model = MixingModel(electrode_name)
    machine = MixingMachine(f"{electrode_name}_Mixer", model, params)

    # Real-time data every 5 seconds
    try:
        machine.batch_id = batch_id
        machine.data_broadcast_interval_sec = 0.1
        machine.data_broadcast_fn = thread_queue_db_data
    except Exception:
        # If older class without attributes, ignore silently
        pass

    try:
        machine.run()
        thread_broadcast(f"--- {electrode_name} Mixing Finished ---")

    except Exception as e:
        thread_broadcast(f"✗ {electrode_name} mixing failed: {str(e)}")

def run_simulation(payload: SimulationInput):
    if not simulation_lock.acquire(blocking=False):
        thread_broadcast("Simulation already in progress.")
        return

    try:
        thread_broadcast("New simulation started.")
        machines = [("Anode", payload.anode), ("Cathode", payload.cathode)]
        for name, slurry in machines:
            run_mixing(name, slurry)
        thread_broadcast("Simulation complete.")


        thread_broadcast("All simulation stages complete.")
    except Exception as e:
        thread_broadcast(f"SIMULATION FAILED: {str(e)}")
    finally:
        simulation_lock.release()

from backend.src.server.db.model_table import create_tables

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    global main_loop
    main_loop = asyncio.get_running_loop()

     # Ensure tables exist
    try:
        create_tables()
        thread_broadcast("✓ Database tables ensured.")
    except Exception as e:
        thread_broadcast(f"✗ Table creation failed: {e}")

    # Start database worker thread
    try:
        db_worker_thread = threading.Thread(target=db_worker, daemon=True)
        db_worker_thread.start()
        thread_broadcast("✓ Database worker started.")
    except Exception as e:
        thread_broadcast(f"✗ Database worker failed to start: {e}")

@app.post("/start-simulation")
def start_simulation(payload: SimulationInput):
    with message_lock:
        message_queue.clear()
    threading.Thread(target=run_simulation, args=(payload,), daemon=True).start()
    return {"message": "Simulation started. See WebSocket for progress."}

@app.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.websocket("/ws/data")
async def websocket_data_endpoint(websocket: WebSocket):
    await data_manager.connect(websocket)
    try:
        while True:
            # Keep the socket alive; client messages are ignored
            await websocket.receive_text()
    except WebSocketDisconnect:
        data_manager.disconnect(websocket)

@app.get("/")
def root():
    try:
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/db/tables")
def list_tables():
    try:
        inspector = sqlalchemy.inspect(engine)
        tables = inspector.get_table_names()
        return {"tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
