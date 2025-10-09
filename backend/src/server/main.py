import os
import sys

# for simulation & concurrency
import threading

# for API
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn

# --- Path and Simulation Module Imports ---
# This points from `backend/src/server` up one level to `backend/src` so that `simulation` can be imported

# Import the core simulation class
from simulation.factory.PlantSimulation import PlantSimulation

# Import websocket manager & database helper (singletons)
from server.websocket_manager import websocket_manager
from server.db.db_helper import database_helper
from server.db.db import engine, SessionLocal
from server.db.model_table import *

# Import event handlers
from server.event_handler import EventHandler

# Import parameter mapping utilities
from server.parameter_mapper import ParameterMapper

from server.logging_helper import configure_logging, get_logger

# initialise logging once for the server process
configure_logging()
logger = get_logger("server")

# Pydantic models for request bodies
class ParameterRequest(BaseModel):
    stage: str
    parameters: Dict[str, float]

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
# Initialise event handler with shared dependencies
event_handler = EventHandler(
    plant_simulation=battery_plant_simulation,
    websocket_manager=websocket_manager,
    database_helper=database_helper,
)

TABLE_MAP = {
    "anode_mixing": AnodeMixing,
    "cathode_mixing": CathodeMixing,
    "anode_coating": AnodeCoating,
    "cathode_coating": CathodeCoating,
    "anode_drying": AnodeDrying,
    "cathode_drying": CathodeDrying,
    "anode_calendaring": AnodeCalendaring,
    "cathode_calendaring": CathodeCalendaring,
    "anode_slitting": AnodeSlitting,
    "cathode_slitting": CathodeSlitting,
    "anode_inspection": AnodeInspection,
    "cathode_inspection": CathodeInspection,
    "rewinding": Rewinding,
    "electrolyte_filling": ElectrolyteFilling,
    "formation_cycling": FormationCycling,
    "aging": Aging,
}

def serialize_row(row):
    """Serialize a SQLAlchemy row to a dict."""
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}

@app.get("/")
def root():
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
    try:
        battery_plant_simulation.add_batch()
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


@app.post("/api/parameters/validate")
def validate_parameters(request_data: ParameterRequest):
    """
    Validate frontend parameters for a specific stage.
    
    Expected format:
    {
        "stage": "Anode Mixing",
        "parameters": {
            "Anode PVDF": 0.05,
            "Anode CA": 0.045,
            "Anode AM": 0.495,
            "Anode Solvent": 0.41
        }
    }
    """
    try:
        stage = request_data.stage
        parameters = request_data.parameters
        
        if not stage:
            raise HTTPException(status_code=400, detail="Stage name is required")
        
        validation_result = ParameterMapper.validate_frontend_parameters(parameters, stage)
        
        if validation_result["valid"]:
            return {
                "valid": True,
                "message": validation_result["message"],
                "stage": stage,
                "line_type": validation_result["line_type"],
                "machine_id": validation_result["machine_id"]
            }
        else:
            return {
                "valid": False,
                "error": validation_result["error"],
                "message": validation_result["message"]
            }
    
    except Exception as e:
        logger.error(f"Parameter validation error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/api/parameters/update")
def update_parameters_from_frontend(request_data: ParameterRequest):
    """
    Update machine parameters using frontend field names.
    
    Expected format:
    {
        "stage": "Anode Mixing",
        "parameters": {
            "Anode PVDF": 0.05,
            "Anode CA": 0.045,
            "Anode AM": 0.495,
            "Anode Solvent": 0.41
        }
    }
    """
    global battery_plant_simulation
    
    try:
        stage = request_data.stage
        parameters = request_data.parameters
        
        if not stage or not parameters:
            raise HTTPException(status_code=400, detail="Stage and parameters are required")
        
        # Validate and convert parameters
        validation_result = ParameterMapper.validate_frontend_parameters(parameters, stage)
        
        if not validation_result["valid"]:
            raise HTTPException(status_code=400, detail=validation_result["error"])
        
        line_type = validation_result["line_type"]
        machine_id = validation_result["machine_id"]
        parameter_obj = validation_result["parameters"]
        
        # Update the machine parameters
        try:
            if battery_plant_simulation.update_machine_parameters(line_type, machine_id, parameter_obj):
                return {
                    "message": f"Parameters updated successfully for {stage}",
                    "stage": stage,
                    "line_type": line_type,
                    "machine_id": machine_id,
                    "updated_parameters": parameter_obj.get_parameters_dict()
                }
        except RuntimeError as e:
            raise HTTPException(status_code=409, detail=str(e))  # Machine busy
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Parameter update error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/api/parameters/current/{stage}")
def get_current_parameters(stage: str):
    """
    Get current parameters for a machine stage.
    Returns parameters in frontend-friendly format.
    """
    global battery_plant_simulation
    
    try:
        # Convert stage to machine info
        line_type, machine_id = ParameterMapper.stage_to_machine_info(stage)
        
        # Get current machine status (includes parameters)
        machine_status = battery_plant_simulation.get_machine_status(line_type, machine_id)
        
        if "machine_parameters" in machine_status:
            return {
                "stage": stage,
                "line_type": line_type,
                "machine_id": machine_id,
                "parameters": machine_status["machine_parameters"],
                "machine_state": machine_status.get("state", "Unknown")
            }
        else:
            raise HTTPException(status_code=404, detail="Machine parameters not found")
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Get parameters error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Startup event to initialise event-driven architecture
@app.on_event("startup")
async def startup_event():
    """Initialise the event-driven architecture."""
    try:
        event_handler.initialise_system_subscriptions()
        logger.info("[startup] Successfully initialised event-driven architecture!")
    except Exception as e:
        logger.exception("[startup] Error initialising event-driven architecture")
        raise
    
    try:
         database_helper.start_worker(lambda msg: print(msg))
         logger.info("Successfully created database helper!")
    except Exception as e:
         logger.error(f"Error creating database helper: {e}")

@app.get("/api/db/{table_name}")
def get_table_entries(table_name: str):
    """Return all entries from the specified table."""
    table_class = TABLE_MAP.get(table_name)
    if not table_class:
        return {"error": f"Table '{table_name}' not found."}
    try:
        db = SessionLocal()
        rows = db.query(table_class).all()
        db.close()
        if not rows:
            return {"message": f"No entries found in {table_name} table.", "data": []}
        return {"data": [serialize_row(row) for row in rows]}
    except Exception as e:
        return {"error": f"Failed to fetch entries from {table_name}: {str(e)}"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
