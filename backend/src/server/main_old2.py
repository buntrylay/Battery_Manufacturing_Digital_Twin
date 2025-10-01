import time
import os
import threading
from collections import deque
from datetime import datetime
from typing import List

import sqlalchemy
from sqlalchemy import Table, Column, Integer, Float, String, MetaData, insert, inspect
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
from simulation.battery_model.MixingModel import MixingModel
from simulation.machine.MixingMachine import MixingMachine

MAX_MESSAGES = 100
message_queue = deque(maxlen=MAX_MESSAGES)
message_lock = threading.Lock()
simulation_lock = threading.Lock()
main_loop = None

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

def thread_broadcast(message: str):
    global main_loop
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    with message_lock:
        message_queue.append(formatted_message)
    if main_loop and main_loop.is_running():
        main_loop.call_soon_threadsafe(manager.broadcast, formatted_message)

class SlurryInput(BaseModel):
    PVDF: float
    CA: float
    AM: float
    Solvent: float

class SimulationInput(BaseModel):
    anode: SlurryInput
    cathode: SlurryInput



def run_machine(process: str, slurry_input: SlurryInput):
    thread_broadcast(f"--- Starting {process} ---")
    model = MixingModel(process)
    params = MixingParameters(
        PVDF=slurry_input.PVDF,
        CA=slurry_input.CA,
        AM=slurry_input.AM,
        solvent=slurry_input.Solvent
    )
    machine = MixingMachine(model, params)
    all_results = machine.run()

    if all_results is None or not isinstance(all_results, list):
        thread_broadcast(f"{process} machine returned no result!")
        return

    for result in all_results:
        result["process"] = process

    # Use the imported function from db.py
    insert_flattened_data(engine, all_results)
    thread_broadcast(f"--- {process} Finished ---")

def run_simulation(payload: SimulationInput):
    if not simulation_lock.acquire(blocking=False):
        thread_broadcast("Simulation already in progress.")
        return

    try:
        thread_broadcast("New simulation started.")
        
        # --- ANODE PRODUCTION ---
        thread_broadcast("--- Starting Anode Mixing Process ---")
        anode_payload = payload.anode
        
        anode_mixing_model = MixingModel("Anode")
        anode_mixing_machine = MixingMachine("Anode_Mixer",
                anode_mixing_model,
                MixingParameters(AM=0.495, CA=0.045, PVDF=0.05, solvent=0.41))
        anode_mixing_machine.run()
        thread_broadcast("--- Anode Mixing Process Finished ---")

        # --- CATHODE PRODUCTION ---
        thread_broadcast("--- Starting Cathode Mixing Process ---")
        cathode_payload = payload.cathode
        
        cathode_mixing_model = MixingModel("Cathode")
        cathode_mixing_machine = MixingMachine("Cathode_Mixer",
            cathode_mixing_model,
            MixingParameters(AM=0.495, CA=0.045, PVDF=0.05, solvent=0.41))
        cathode_mixing_machine.run()
        thread_broadcast("--- Cathode Mixing Process Finished ---")

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

@app.post("/start-simulation")
def start_simulation(payload: SimulationInput):
    global message_queue
    with message_lock:
        message_queue.clear()  # Clear previous logs
    threading.Thread(target=run_simulation, args=(payload,)).start()
    return {"message": "Simulation started. See WebSocket for progress."}


@app.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
POSTGRES_DB = os.getenv("POSTGRES_DB", "postgres")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = "postgresql://postgres:password@localhost/postgres"
engine = sqlalchemy.create_engine(DATABASE_URL)

@app.get("/")
def root():
    try:
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
            print("Database connection successful.")
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        print(f"Database connection failed: {e}")
