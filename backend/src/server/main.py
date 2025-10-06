import os
import sys

# for async tasks
import asyncio

# for simulation & concurrency
import threading

# for API
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json

# for generation of unique batch ID
import uuid

# --- Path and Simulation Module Imports ---
# This points from `backend/src/server` up one level to `backend/src` so that `simulation` can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the core simulation class
from simulation.factory.Batch import Batch
from simulation.factory.PlantSimulation import PlantSimulation

# Import websocket manager
from .WebSocketManager import websocket_manager

# Import event handlers
from .event_handler import EventHandler

# Import database engine & session
from backend.src.server.db.db import engine
from backend.src.server.db.model_table import *
from backend.src.server.db.db_helper import DBHelper
import sqlalchemy

# main FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# core plant simulation object
battery_plant_simulation = PlantSimulation()
# regarding the simulation thread
factory_run_thread = None
out_of_batch_event = threading.Event()
# WebSocket connection management
db_helper = DBHelper()
# Initialise event handler
event_handler = EventHandler()


@app.get("/")
def root():
    try:
        # what is this for? Health check?
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "This is the V2 API for the battery manufacturing digital twin!"}


@app.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time machine status updates."""
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive and handle any incoming messages
            data = await websocket.receive_text()
            # Echo back any received messages (optional)
            await websocket_manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)


@app.get("/api/simulation/state")
def get_plant_state():
    """Get the current state of the plant. Returns a dictionary with the current state of the plant."""
    # quite done, just some validation I think depending on my teammate's implementation of get_current_plant_state()
    global battery_plant_simulation
    return battery_plant_simulation.get_current_plant_state()


@app.post("/api/simulation/start")
def add_batch():
    """Add a batch to the plant."""
    global battery_plant_simulation
    global factory_run_thread
    global out_of_batch_event
    batch = Batch(batch_id=str(uuid.uuid4()))
    try:
        battery_plant_simulation.add_batch(batch)
    except ValueError as e:
        # over limit of batches
        raise HTTPException(status_code=400, detail=str(e))
    if factory_run_thread is None:
        factory_run_thread = threading.Thread(
            target=battery_plant_simulation.run, args=(out_of_batch_event,)
        )
        factory_run_thread.start()
    elif out_of_batch_event.is_set():
        factory_run_thread = None
        out_of_batch_event.clear()
        factory_run_thread = threading.Thread(
            target=battery_plant_simulation.run, args=(out_of_batch_event,)
        )
        factory_run_thread.start()
        return {"message": "Plant started successfully"}


@app.get("/api/machine/{line_type}/{machine_id}/status")
def get_machine_status(line_type: str, machine_id: str):
    """Get the status of a machine. Returns a dictionary with the status of the machine."""
    # quite done, just some validation I think depending on my teammate's implementation of get_machine_status()
    global battery_plant_simulation
    try:
        return battery_plant_simulation.get_machine_status(line_type, machine_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.patch("/api/machine/{line_type}/{machine_id}/parameters")
def update_machine_params(line_type: str, machine_id: str, parameters: dict):
    """Update machine parameters with validation."""
    global battery_plant_simulation
    try:
        # Delegate validation to PlantSimulation / Machine classes
        if battery_plant_simulation.update_machine_parameters(
            line_type, machine_id, parameters
        ):
            return {
                "message": f"Machine {machine_id} parameters updated successfully",
                "line_type": line_type,
                "machine_id": machine_id,
            }
    except TypeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/simulation/reset")
def reset_plant():
    """Reset the plant."""
    global battery_plant_simulation
    global factory_run_thread
    global out_of_batch_event
    # reset the factory run thread
    if factory_run_thread:
        factory_run_thread.join()
        factory_run_thread = None
    # reset the plant simulation object
    battery_plant_simulation.reset_plant()
    # reset the event
    if out_of_batch_event.is_set():
        out_of_batch_event.clear()
    return {"message": "Plant reset successfully"}


# Startup event to initialise event-driven architecture
@app.on_event("startup")
async def startup_event():
    """Initialise the event-driven architecture."""
    try:
        # Get event bus from plant simulation
        event_bus = battery_plant_simulation.get_event_bus()
        # Set up WebSocket manager to subscribe to events
        websocket_manager.set_event_bus(event_bus, event_handler)
        # Set up DB helper to subscribe to events
        db_helper.set_event_bus(event_bus, event_handler)
        print("Successfully initialized event-driven architecture!")
    except Exception as e:
        print(f"Error initializing event-driven architecture: {e}")
    try:
        create_tables()
        print(f"Successfully populated tables!")
    except Exception as e:
        print(f"Error populating tables: {e}")
    try:
        db_helper.start_worker(lambda msg: print(msg))
        print(f"Successfully created db helper!")
    except Exception as e:
        print(f"Error creating db helper: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
