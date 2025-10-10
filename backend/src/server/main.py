from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import the core simulation class

from simulation.factory.PlantSimulation import PlantSimulation

# Import websocket manager & database helper (singletons)
from server.websocket_manager import websocket_manager
from server.db.db_helper import database_helper
from server.db.db import SessionLocal
from server.db.model_table import *

# Import event handlers
from server.event_handler import EventHandler

# Import parameter mapping utilities
from server.logging_helper import configure_logging, get_logger
from server.parameter_mapper import ParameterMapper

# import format utilities
from server.format_helper import create_error_response, create_success_response

# Initialise logging once for the server process
configure_logging()
logger = get_logger("server")

# Core plant simulation object
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
    except Exception:
        logger.exception("[startup] Error initialising event-driven architecture")
        raise SystemError()
    try:
        database_helper.start_worker(lambda msg: print(msg))
        logger.info("[startup] Successfully created database helper!")
    except Exception as db_exc:
        logger.error(f"[startup] Error creating database helper: {db_exc}")
    # try: maybe some check to WebSocket server
    #     logger.info("[startup] Successfully created WebSocket server!")
    # except Exception as websocket_exc:
    #     logger.error(
    #         f"[startup] Error setting up WebSocket server: {websocket_exc}"
    #     )
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


# === New Parameter Management Endpoints ===

@app.post("/api/parameters/validate")
def validate_parameters(request_data: dict):
    """Validate machine parameters using frontend stage names."""
    try:
        stage = request_data.get("stage")
        parameters = request_data.get("parameters", {})
        
        # Log the incoming request for debugging
        logger.info(f"Validation request - Stage: {stage}, Parameters: {parameters}")
        
        if not stage:
            raise HTTPException(
                status_code=400,
                detail=create_error_response("Stage name is required", error_code="MISSING_STAGE")
            )
        
        # Use ParameterMapper to validate
        validation_result = ParameterMapper.validate_frontend_parameters(parameters, stage)
        
        # Log the validation result
        logger.info(f"Validation result: {validation_result}")
        
        if validation_result["valid"]:
            return create_success_response(
                validation_result["message"],
                data={
                    "valid": True,
                    "line_type": validation_result["line_type"],
                    "machine_id": validation_result["machine_id"]
                }
            )
        else:
            return create_error_response(
                validation_result["message"],
                error_code="VALIDATION_FAILED",
                errors=validation_result.get("error")
            )
            
    except Exception as e:
        logger.error(f"Parameter validation error: {e}")
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                f"Parameter validation failed: {str(e)}",
                error_code="VALIDATION_ERROR"
            )
        )


@app.post("/api/parameters/update")
def update_parameters_by_stage(request_data: dict):
    """Update machine parameters using frontend stage names."""
    global battery_plant_simulation
    
    try:
        stage = request_data.get("stage")
        parameters = request_data.get("parameters", {})
        
        if not stage:
            raise HTTPException(
                status_code=400,
                detail=create_error_response("Stage name is required", error_code="MISSING_STAGE")
            )
        
        # First validate the parameters
        validation_result = ParameterMapper.validate_frontend_parameters(parameters, stage)
        
        if not validation_result["valid"]:
            raise HTTPException(
                status_code=400,
                detail=create_error_response(
                    validation_result["message"],
                    error_code="VALIDATION_FAILED",
                    errors=validation_result.get("error")
                )
            )
        
        # Convert frontend parameters to backend format
        line_type, machine_id = ParameterMapper.stage_to_machine_info(stage)
        backend_params = ParameterMapper.frontend_to_backend_parameters(parameters, machine_id)
        
        # Update the machine parameters
        if battery_plant_simulation.update_machine_parameters(line_type, machine_id, backend_params):
            return create_success_response(
                f"Parameters for {stage} updated successfully",
                data={
                    "stage": stage,
                    "line_type": line_type,
                    "machine_id": machine_id,
                    "updated_parameters": list(backend_params.keys())
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=create_error_response(
                    "Failed to update machine parameters",
                    error_code="UPDATE_FAILED"
                )
            )
            
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                str(e),
                error_code="PARAMETER_VALUE_ERROR"
            )
        )
    except TimeoutError as e:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                str(e),
                error_code="MACHINE_BUSY"
            )
        )
    except Exception as e:
        logger.error(f"Parameter update error: {e}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                f"Parameter update failed: {str(e)}",
                error_code="UPDATE_ERROR"
            )
        )


@app.get("/api/parameters/current/{stage}")
def get_current_parameters(stage: str):
    """Get current parameters for a machine stage."""
    global battery_plant_simulation
    
    try:
        # Convert stage name to line_type and machine_id
        line_type, machine_id = ParameterMapper.stage_to_machine_info(stage)
        
        # Get machine status which includes current parameters
        machine_status = battery_plant_simulation.get_machine_status(line_type, machine_id)
        
        return create_success_response(
            f"Current parameters for {stage} retrieved successfully",
            data={
                "stage": stage,
                "line_type": line_type,
                "machine_id": machine_id,
                "parameters": machine_status.get("machine_parameters", {}),
                "status": machine_status
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                str(e),
                error_code="INVALID_STAGE"
            )
        )
    except Exception as e:
        logger.error(f"Get current parameters error: {e}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                f"Failed to get current parameters: {str(e)}",
                error_code="GET_PARAMETERS_ERROR"
            )
        )


@app.post("/api/simulation/mixing/start") 
def start_mixing_simulation(request_data: dict = None):
    """Start mixing simulation for specific electrode type."""
    global battery_plant_simulation
    
    try:
        # For now, this will work the same as regular simulation start
        # In the future, you could add specific mixing logic here
        electrode_type = request_data.get("electrode_type") if request_data else None
        
        batch_id = battery_plant_simulation.add_batch()
        
        message = "Mixing simulation started successfully"
        if electrode_type:
            message = f"Mixing simulation for {electrode_type} started successfully"
            
        return create_success_response(
            message,
            data={
                "batch_id": batch_id,
                "electrode_type": electrode_type
            }
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=create_error_response(str(e), error_code="BATCH_LIMIT")
        )
    except Exception as e:
        logger.error(f"Mixing simulation start error: {e}")
        raise HTTPException(
            status_code=500,
            detail=create_error_response(
                f"Failed to start mixing simulation: {str(e)}",
                error_code="MIXING_START_ERROR"
            )
        )


# === Backward Compatibility Endpoints ===

@app.post("/reset")
def reset_simulation_legacy():
    """Legacy reset endpoint for backward compatibility."""
    return reset_plant()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
