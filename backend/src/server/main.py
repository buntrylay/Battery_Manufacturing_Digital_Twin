import os
import sys
import shutil
import threading
import asyncio
from pathlib import Path
from zipfile import ZipFile
from collections import deque
from datetime import datetime
from typing import List

 
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from simulation.battery_model.MixingModel import MixingModel
from simulation.machine.MixingMachine import MixingMachine, MixingParameters, MaterialRatios
from simulation.factory.Factory import Factory

# --- Path and Simulation Module Imports ---
# This points from `backend/src/server` up two levels to the project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
 
# Import the machine and model classes directly
from simulation.battery_model.MixingModel import MixingModel
from simulation.machine.MixingMachine import MixingMachine, MixingParameters, MaterialRatios
 
# --- WebSocket and Message Queue Setup ---
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
            except Exception: pass
 
manager = ConnectionManager()
 
def thread_broadcast(message: str):
    global main_loop
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_message = f"[{timestamp}] {message}"
    
    with message_lock:
        message_queue.append(formatted_message)
    
    if main_loop and main_loop.is_running():
        main_loop.call_soon_threadsafe(manager.broadcast, formatted_message)
 
# --- FastAPI Application Setup ---
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
RESULTS_PATH = Path("results")
RESULTS_PATH.mkdir(parents=True, exist_ok=True)
 
# --- Pydantic Models for API Input ---
class SlurryInput(BaseModel):
    PVDF: float
    CA: float
    AM: float
    Solvent: float
 
class SimulationInput(BaseModel):
    anode: SlurryInput
    cathode: SlurryInput
 
# --- Corrected Simulation Logic ---
def run_simulation(payload: SimulationInput):
    if not simulation_lock.acquire(blocking=False):
        thread_broadcast("ERROR: A simulation is already in progress.")
        return
 
    try:
        thread_broadcast("✅ New simulation started.")
        
        # --- ANODE PRODUCTION ---
        thread_broadcast("--- Starting Anode Mixing Process ---")
        anode_payload = payload.anode
        
        anode_mixing_model = MixingModel("Anode")
        anode_mixing_params = MixingParameters(
            material_ratios=MaterialRatios(
                PVDF=anode_payload.PVDF,
                CA=anode_payload.CA,
                AM=anode_payload.AM,
                solvent=anode_payload.Solvent
            )
        )
        anode_mixer = MixingMachine(anode_mixing_model, anode_mixing_params)
        anode_mixer.run()
        thread_broadcast("--- Anode Mixing Process Finished ---")
 
        # --- CATHODE PRODUCTION ---
        thread_broadcast("--- Starting Cathode Mixing Process ---")
        cathode_payload = payload.cathode
        
        cathode_mixing_model = MixingModel("Cathode")
        cathode_mixing_params = MixingParameters(
            material_ratios=MaterialRatios(
                PVDF=cathode_payload.PVDF,
                CA=cathode_payload.CA,
                AM=cathode_payload.AM,
                solvent=cathode_payload.Solvent
            )
        )
        cathode_mixer = MixingMachine(cathode_mixing_model, cathode_mixing_params)
        cathode_mixer.run()
        thread_broadcast("--- Cathode Mixing Process Finished ---")
 
        thread_broadcast("✅ All simulation stages complete.")
 
    except Exception as e:
        thread_broadcast(f"❌ SIMULATION FAILED: {str(e)}")
    finally:
        simulation_lock.release()
 
# --- API Endpoints ---
@app.on_event("startup")
async def startup_event():
    global main_loop
    main_loop = asyncio.get_running_loop()
 
@app.post("/start-simulation")
def start_simulation(payload: SimulationInput):
    simulation_thread = threading.Thread(target=run_simulation, args=(payload,))
    simulation_thread.start()
    return {"message": "Simulation started. See progress via WebSocket."}
 
@app.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)