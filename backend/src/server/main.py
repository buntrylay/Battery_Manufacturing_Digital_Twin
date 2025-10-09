import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uvicorn

# Import websocket manager & database helper (singletons)
from .websocket_manager import websocket_manager
from .db.db_helper import database_helper

# Import event handlers
from .event_handler import EventHandler

# Import helpers
from .logging_helper import configure_logging, get_logger
from .format_helper import create_error_response, create_success_response

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

# core plant simulation object
battery_plant_simulation = PlantSimulation()
# Initialise event handler with shared dependencies
event_handler = EventHandler(
    plant_simulation=battery_plant_simulation,
    websocket_manager=websocket_manager,
    database_helper=database_helper,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage startup and shutdown tasks for the FastAPI application."""
    try:
        event_handler.initialise_system_subscriptions()
        logger.info("[startup] Successfully initialised event-driven architecture!")
        # try:
        #     database_helper.start_worker(lambda msg: print(msg))
        #     logger.info("Successfully created database helper!")
        # except Exception as db_exc:
        #     logger.error(f"Error creating database helper: {db_exc}")
    except Exception:
        logger.exception("[startup] Error initialising event-driven architecture")
        raise
    try:
        yield
    finally:
        # Placeholder for future shutdown/cleanup logic.
        pass


# main FastAPI app
app = FastAPI(lifespan=lifespan)
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
    """Entry of the web server"""
    return create_success_response(
        "This is the V2 API for the battery manufacturing digital twin!"
    )


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
    plant_state = battery_plant_simulation.get_current_plant_state()
    return create_success_response("Plant state is retrieved.", data=plant_state)


@app.post("/api/simulation/start")
def add_batch():
    """Add a batch to the plant. Returns the generated batch ID to the requester."""
    global battery_plant_simulation
    try:
        batch_id = battery_plant_simulation.add_batch()
    except ValueError as e:
        # over limit of batches
        raise HTTPException(
            status_code=400,
            detail=create_error_response(str(e), error_code="BATCH_LIMIT"),
        )
    return create_success_response(
        "A new batch was received and added to processing queue.",
        batch_id=batch_id,
    )


@app.get("/api/machine/{line_type}/{machine_id}/status")
def get_machine_status(line_type: str, machine_id: str):
    """Get the status of a machine. Returns a dictionary with the status of the machine."""
    # quite done, just some validation I think depending on my teammate's implementation of get_machine_status()
    global battery_plant_simulation
    try:
        status = battery_plant_simulation.get_machine_status(line_type, machine_id)
        return create_success_response(
            f"Machine {line_type} {machine_id}'s status was successfully retrieved.",
            line_type=line_type,
            machine_id=machine_id,
            data=status,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                str(e),
                error_code="MACHINE_NOT_FOUND",
                line_type=line_type,
                machine_id=machine_id,
            ),
        )


@app.patch("/api/machine/{line_type}/{machine_id}/parameters")
def update_machine_params(line_type: str, machine_id: str, parameters: dict):
    """Update machine parameters with validation."""
    global battery_plant_simulation
    try:
        # Delegate validation to PlantSimulation / Machine classes
        if battery_plant_simulation.update_machine_parameters(
            line_type, machine_id, parameters
        ):
            return create_success_response(
                f"Machine {machine_id}'s parameters were updated successfully",
                line_type=line_type,
                machine_id=machine_id,
            )
    except TypeError as e:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                str(e),
                error_code="MACHINE_PARAMETER_TYPE_ERROR",
                line_type=line_type,
                machine_id=machine_id,
            ),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                str(e),
                error_code="MACHINE_PARAMETER_VALIDATION_ERROR",
                line_type=line_type,
                machine_id=machine_id,
            ),
        )


@app.post("/api/simulation/reset")
def reset_plant():
    """Reset the plant."""
    global battery_plant_simulation
    try:
        battery_plant_simulation.reset_plant()
        return create_success_response("Plant was reset successfully.")
    except TimeoutError as e:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(str(e), error_code="RESET_TIMEOUT"),
        )

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
