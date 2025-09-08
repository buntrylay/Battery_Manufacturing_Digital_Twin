import asyncio
from datetime import datetime
from collections import deque
from typing import List
import threading

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from server.db import engine, insert_flattened_data
from simulation.battery_model.MixingModel import MixingModel
from simulation.machine.MixingMachine import MixingMachine, MixingParameters, MaterialRatios

# --- WebSocket & Queue ---
MAX_MESSAGES = 100
message_queue = deque(maxlen=MAX_MESSAGES)
message_lock = threading.Lock()
simulation_lock = threading.Lock()
main_loop = None

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        with message_lock:
            for msg in message_queue:
                await websocket.send_text(msg)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                asyncio.ensure_future(connection.send_text(message))
            except Exception:
                pass

manager = ConnectionManager()

def thread_broadcast(message: str):
    global main_loop
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    
    with message_lock:
        message_queue.append(formatted_message)
    
    if main_loop and main_loop.is_running():
        main_loop.call_soon_threadsafe(manager.broadcast, formatted_message)

# --- FastAPI App ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class SlurryInput(BaseModel):
    PVDF: float
    CA: float
    AM: float
    Solvent: float

class SimulationInput(BaseModel):
    anode: SlurryInput
    cathode: SlurryInput

# --- Machine Runner ---
def run_machine(machine_name: str, slurry_input: SlurryInput):
    thread_broadcast(f"--- Starting {machine_name} Process ---")
    model = MixingModel(machine_name)
    params = MixingParameters(
        material_ratios=MaterialRatios(
            PVDF=slurry_input.PVDF,
            CA=slurry_input.CA,
            AM=slurry_input.AM,
            solvent=slurry_input.Solvent
        )
    )
    machine = MixingMachine(model, params)
    result = machine.run()

    # --- Insert into dynamic machine-specific table ---
    insert_flattened_data(engine, machine_name.lower(), result)
    thread_broadcast(f"--- {machine_name} Process Finished ---")

# --- Simulation Runner ---
def run_simulation(payload: SimulationInput):
    if not simulation_lock.acquire(blocking=False):
        thread_broadcast("ERROR: Simulation already in progress.")
        return

    try:
        thread_broadcast("✅ New simulation started.")
        machines = [
            ("Anode", payload.anode),
            ("Cathode", payload.cathode),
        ]
        for name, slurry in machines:
            run_machine(name, slurry)
        thread_broadcast("✅ All simulation stages complete.")
    except Exception as e:
        thread_broadcast(f"❌ SIMULATION FAILED: {str(e)}")
    finally:
        simulation_lock.release()

# --- FastAPI Events & Endpoints ---
@app.on_event("startup")
async def startup_event():
    global main_loop
    main_loop = asyncio.get_running_loop()

@app.post("/start-simulation")
def start_simulation(payload: SimulationInput):
    """Start simulation in a separate thread"""
    threading.Thread(target=run_simulation, args=(payload,)).start()
    return {"message": "Simulation started. See progress via WebSocket."}

@app.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)
