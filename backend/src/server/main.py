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
from backend.src.server.db.db_helper import DBHelper

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
db_helper = DBHelper()

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
        machine.data_broadcast_fn = db_helper.queue_data
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
        db_helper.start_worker(thread_broadcast)
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
