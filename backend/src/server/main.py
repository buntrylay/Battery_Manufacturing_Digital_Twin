import os
import sys
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

# Import notification queue
from .notification_queue import notification_queue, notify_machine_status
from .WebSockerManager import manager

# Import database engine & session
from backend.src.server.db.db import engine, SessionLocal
from backend.src.server.db.model_table import *
from backend.src.server.db.db_helper import DBHelper
import sqlalchemy

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

battery_plant_simulation = PlantSimulation()
factory_run_thread = None
out_of_batch_event = threading.Event()


# WebSocket connection management

db_helper = DBHelper()

@app.get("/")
def root():
    try:
        with engine.connect() as conn:
            conn.execute(sqlalchemy.text("SELECT 1"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"message": "This is the V2 API for the battery manufacturing digital twin!"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": "2025-10-01T16:00:00Z"}


@app.websocket("/ws/status")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time machine status updates."""
    await manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive and handle any incoming messages
            data = await websocket.receive_text()
            # Echo back any received messages (optional)
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/api/simulation/state")
def get_plant_state():
    """Get the current state of the plant. Returns a dictionary with the current state of the plant."""
    # quite done, just some validation I think depending on my teammate's implementation of get_current_plant_state()
    global battery_plant_simulation
    return battery_plant_simulation.get_current_plant_state()


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

def convert_numpy_types(obj):
    import numpy as np
    
    if isinstance(obj, dict):
        return {k: convert_numpy_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(v) for v in obj]
    elif isinstance(obj, np.generic):
        return obj.item()
    else:
        return obj

# Background task to process notifications and broadcast to WebSocket clients
async def process_notifications():
    
    """Background task to process machine notifications and broadcast to WebSocket clients."""
    while True:
        try:
            # Get notification from queue
            notification = await notification_queue.get_notification()
            
            # If this is a data notification, queue for DB writing
            if notification.status == "data_generated":
                # Merge notification fields with data
                db_helper.queue_data(notification.data)
                print("Generated data pushed to db helper queue!")
                continue


            # Convert to JSON and broadcast to all connected clients
            message = json.dumps(notification.to_dict())
            await manager.broadcast(message)
            
        except Exception as e:
            print(f"Error processing notification: {e}")
            # Small delay to prevent busy waiting
            await asyncio.sleep(0.1)


# Startup event to start the notification processor
@app.on_event("startup")
async def startup_event():
    """Start the background task for processing notifications."""
    asyncio.create_task(process_notifications())

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
