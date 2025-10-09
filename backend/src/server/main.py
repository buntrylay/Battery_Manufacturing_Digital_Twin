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


@app.post("/api/simulation/start")
def start_unified_simulation(simulation_data: dict):
    """Start simulation with parameters for all machine types - unified endpoint."""
    global battery_plant_simulation
    global factory_run_thread
    global out_of_batch_event
    
    try:
        # Import all parameter classes
        from simulation.process_parameters.Parameters import (
            CoatingParameters, DryingParameters, CalendaringParameters, 
            SlittingParameters, ElectrodeInspectionParameters, RewindingParameters,
            ElectrolyteFillingParameters, FormationCyclingParameters, AgingParameters
        )
        
        # Determine simulation mode: 'full' (factory simulation) or 'individual' (single machine)
        mode = simulation_data.get("mode", "full")
        
        if mode == "full":
            # Full factory simulation (existing functionality)
            return _start_full_factory_simulation(simulation_data)
        
        elif mode == "individual":
            # Individual machine simulation
            return _start_individual_machine_simulation(simulation_data)
        
        else:
            raise HTTPException(status_code=400, detail="Mode must be 'full' or 'individual'")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def _start_full_factory_simulation(simulation_data: dict):
    """Start full factory simulation with all machine parameters."""
    global battery_plant_simulation, factory_run_thread, out_of_batch_event
    
    # Import parameter classes
    from simulation.process_parameters.Parameters import (
        CoatingParameters, DryingParameters, CalendaringParameters, 
        SlittingParameters, ElectrodeInspectionParameters, RewindingParameters,
        ElectrolyteFillingParameters, FormationCyclingParameters, AgingParameters
    )
    
    # Extract mixing parameters (required)
    anode_params = simulation_data.get("anode_params")
    cathode_params = simulation_data.get("cathode_params")
    
    if not anode_params or not cathode_params:
        raise HTTPException(
            status_code=400, 
            detail="Both anode_params and cathode_params are required for full simulation"
        )
    
    # Validate mixing parameters
    required_mixing_fields = ["PVDF", "CA", "AM", "Solvent"]
    for field in required_mixing_fields:
        if field not in anode_params:
            raise HTTPException(status_code=400, detail=f"Missing required anode mixing field: {field}")
        if field not in cathode_params:
            raise HTTPException(status_code=400, detail=f"Missing required cathode mixing field: {field}")
    
    # Check mixing ratios sum to 1.0
    anode_total = sum(anode_params[field] for field in required_mixing_fields)
    cathode_total = sum(cathode_params[field] for field in required_mixing_fields)
    
    if abs(anode_total - 1.0) > 0.0001:
        raise HTTPException(status_code=400, detail=f"Anode mixing ratios must sum to 1.0, got {anode_total}")
    if abs(cathode_total - 1.0) > 0.0001:
        raise HTTPException(status_code=400, detail=f"Cathode mixing ratios must sum to 1.0, got {cathode_total}")
    
    # Update machine parameters if provided (optional for full simulation)
    all_parameters = {}
    
    # Extract and validate all machine parameters if provided
    machine_params = {
        "coating_params": CoatingParameters,
        "drying_params": DryingParameters, 
        "calendaring_params": CalendaringParameters,
        "slitting_params": SlittingParameters,
        "inspection_params": ElectrodeInspectionParameters,
        "rewinding_params": RewindingParameters,
        "electrolyte_filling_params": ElectrolyteFillingParameters,
        "formation_cycling_params": FormationCyclingParameters,
        "aging_params": AgingParameters
    }
    
    for param_key, param_class in machine_params.items():
        if param_key in simulation_data:
            try:
                validated_params = param_class(**simulation_data[param_key])
                validated_params.validate_parameters()
                all_parameters[param_key] = simulation_data[param_key]
            except (TypeError, ValueError) as e:
                raise HTTPException(status_code=400, detail=f"Invalid {param_key}: {str(e)}")
    
    # Update machine parameters in plant simulation if provided
    if all_parameters:
        try:
            _update_plant_machine_parameters(all_parameters)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to update machine parameters: {str(e)}")
    
    # Create batch and start factory simulation
    batch = Batch(
        batch_id=str(uuid.uuid4()),
        anode_mixing_params=anode_params,
        cathode_mixing_params=cathode_params
    )
    
    battery_plant_simulation.add_batch(batch)
    
    # Start factory simulation thread
    if factory_run_thread is None:
        factory_run_thread = threading.Thread(target=battery_plant_simulation.run, args=(out_of_batch_event,))
        factory_run_thread.start()
    elif out_of_batch_event.is_set():
        factory_run_thread = None
        out_of_batch_event.clear()
        factory_run_thread = threading.Thread(target=battery_plant_simulation.run, args=(out_of_batch_event,))
        factory_run_thread.start()
    
    return {
        "message": "Full factory simulation started successfully",
        "mode": "full",
        "batch_id": batch.batch_id,
        "anode_params": anode_params,
        "cathode_params": cathode_params,
        "updated_machine_params": list(all_parameters.keys()) if all_parameters else []
    }


def _start_individual_machine_simulation(simulation_data: dict):
    """Start individual machine simulation."""
    machine_type = simulation_data.get("machine_type")
    electrode_type = simulation_data.get("electrode_type")  # Optional for some machines
    parameters = simulation_data.get("parameters", {})
    
    if not machine_type:
        raise HTTPException(status_code=400, detail="machine_type is required for individual simulation")
    
    if not parameters:
        raise HTTPException(status_code=400, detail="parameters are required for individual simulation")
    
    # Map machine types to their simulation functions
    machine_simulators = {
        "mixing": lambda: _run_individual_mixing(electrode_type, parameters),
        "coating": lambda: _run_individual_coating(electrode_type, parameters),
        "drying": lambda: _run_individual_drying(electrode_type, parameters),
        "calendaring": lambda: _run_individual_calendaring(electrode_type, parameters),
        "slitting": lambda: _run_individual_slitting(electrode_type, parameters),
        "inspection": lambda: _run_individual_inspection(electrode_type, parameters),
        "rewinding": lambda: _run_individual_rewinding(parameters),
        "electrolyte_filling": lambda: _run_individual_electrolyte_filling(parameters),
        "formation_cycling": lambda: _run_individual_formation_cycling(parameters),
        "aging": lambda: _run_individual_aging(parameters),
    }
    
    simulator = machine_simulators.get(machine_type)
    if not simulator:
        raise HTTPException(status_code=400, detail=f"Unknown machine_type: {machine_type}")
    
    # Start the individual simulation
    result = simulator()
    
    return {
        "message": f"Individual {machine_type} simulation started successfully",
        "mode": "individual", 
        "machine_type": machine_type,
        "electrode_type": electrode_type,
        "parameters": parameters,
        **result
    }


def _update_plant_machine_parameters(all_parameters: dict):
    """Update machine parameters in the plant simulation."""
    global battery_plant_simulation
    
    # Map parameter keys to machine identifiers
    param_to_machine_map = {
        "coating_params": [("anode", "coating"), ("cathode", "coating")],
        "drying_params": [("anode", "drying"), ("cathode", "drying")],
        "calendaring_params": [("anode", "calendaring"), ("cathode", "calendaring")],
        "slitting_params": [("anode", "slitting"), ("cathode", "slitting")],
        "inspection_params": [("anode", "inspection"), ("cathode", "inspection")],
        "rewinding_params": [("cell", "rewinding")],
        "electrolyte_filling_params": [("cell", "electrolyte_filling")],
        "formation_cycling_params": [("cell", "formation_cycling")],
        "aging_params": [("cell", "aging")]
    }
    
    for param_key, params in all_parameters.items():
        machine_mappings = param_to_machine_map.get(param_key, [])
        for line_type, machine_id in machine_mappings:
            try:
                battery_plant_simulation.update_machine_parameters(line_type, machine_id, params)
            except Exception as e:
                print(f"Warning: Could not update {line_type}/{machine_id}: {str(e)}")


# Individual machine simulation helper functions
def _run_individual_mixing(electrode_type, parameters):
    """Run individual mixing simulation."""
    if not electrode_type or electrode_type not in ["Anode", "Cathode"]:
        raise HTTPException(status_code=400, detail="electrode_type must be 'Anode' or 'Cathode' for mixing")
    
    # Validate mixing parameters
    required_fields = ["PVDF", "CA", "AM", "Solvent"]
    for field in required_fields:
        if field not in parameters:
            raise HTTPException(status_code=400, detail=f"Missing required mixing field: {field}")
    
    total = sum(parameters[field] for field in required_fields)
    if abs(total - 1.0) > 0.0001:
        raise HTTPException(status_code=400, detail=f"Mixing ratios must sum to 1.0, got {total}")
    
    # Start mixing simulation in background (reuse existing logic)
    def run_mixing():
        try:
            from simulation.machine.MixingMachine import MixingMachine
            from simulation.battery_model.MixingModel import MixingModel
            from simulation.process_parameters.MixingParameters import MixingParameters, MaterialRatios
            
            machine_id = f"{electrode_type.lower()}_mixing_01"
            process_name = f"{electrode_type}_Mixing"
            
            notify_machine_status(machine_id=machine_id, line_type="mixing", process_name=process_name,
                                status="running", data={"message": f"Starting {electrode_type} mixing", "parameters": parameters})
            
            mixing_model = MixingModel(electrode_type)
            material_ratios = MaterialRatios(AM=parameters["AM"], CA=parameters["CA"], 
                                           PVDF=parameters["PVDF"], solvent=parameters["Solvent"])
            mixing_parameters = MixingParameters(material_ratios=material_ratios)
            
            mixing_machine = MixingMachine(process_name=process_name, mixing_model=mixing_model, mixing_parameters=mixing_parameters)
            mixing_machine.receive_model_from_previous_process(mixing_model)
            mixing_machine.run()
            
            notify_machine_status(machine_id=machine_id, line_type="mixing", process_name=process_name,
                                status="completed", data={"message": f"{electrode_type} mixing completed", "results": mixing_machine.get_current_state()})
        except Exception as e:
            notify_machine_status(machine_id=machine_id, line_type="mixing", process_name=process_name,
                                status="error", data={"message": f"Mixing failed: {str(e)}"})
    
    simulation_thread = threading.Thread(target=run_mixing)
    simulation_thread.daemon = True
    simulation_thread.start()
    
    return {"simulation_started": True}


def _run_individual_coating(electrode_type, parameters):
    """Run individual coating simulation."""
    if not electrode_type or electrode_type not in ["Anode", "Cathode"]:
        raise HTTPException(status_code=400, detail="electrode_type must be 'Anode' or 'Cathode' for coating")
    
    from simulation.process_parameters.Parameters import CoatingParameters
    coating_params = CoatingParameters(**parameters)
    coating_params.validate_parameters()
    
    def run_coating():
        try:
            from simulation.machine.CoatingMachine import CoatingMachine
            machine_id = f"{electrode_type.lower()}_coating_01"
            process_name = f"{electrode_type}_Coating"
            
            notify_machine_status(machine_id=machine_id, line_type="coating", process_name=process_name,
                                status="running", data={"message": f"Starting {electrode_type} coating", "parameters": parameters})
            
            coating_machine = CoatingMachine(process_name=process_name, coating_parameters=coating_params)
            coating_machine.run()
            
            notify_machine_status(machine_id=machine_id, line_type="coating", process_name=process_name,
                                status="completed", data={"message": f"{electrode_type} coating completed", "results": coating_machine.get_current_state()})
        except Exception as e:
            notify_machine_status(machine_id=machine_id, line_type="coating", process_name=process_name,
                                status="error", data={"message": f"Coating failed: {str(e)}"})
    
    simulation_thread = threading.Thread(target=run_coating)
    simulation_thread.daemon = True
    simulation_thread.start()
    return {"simulation_started": True}


def _run_individual_drying(electrode_type, parameters):
    """Run individual drying simulation."""
    if not electrode_type or electrode_type not in ["Anode", "Cathode"]:
        raise HTTPException(status_code=400, detail="electrode_type must be 'Anode' or 'Cathode' for drying")
    
    from simulation.process_parameters.Parameters import DryingParameters
    drying_params = DryingParameters(**parameters)
    drying_params.validate_parameters()
    
    def run_drying():
        try:
            from simulation.machine.DryingMachine import DryingMachine
            machine_id = f"{electrode_type.lower()}_drying_01"
            process_name = f"{electrode_type}_Drying"
            
            notify_machine_status(machine_id=machine_id, line_type="drying", process_name=process_name,
                                status="running", data={"message": f"Starting {electrode_type} drying", "parameters": parameters})
            
            drying_machine = DryingMachine(process_name=process_name, drying_parameters=drying_params)
            drying_machine.run()
            
            notify_machine_status(machine_id=machine_id, line_type="drying", process_name=process_name,
                                status="completed", data={"message": f"{electrode_type} drying completed", "results": drying_machine.get_current_state()})
        except Exception as e:
            notify_machine_status(machine_id=machine_id, line_type="drying", process_name=process_name,
                                status="error", data={"message": f"Drying failed: {str(e)}"})
    
    simulation_thread = threading.Thread(target=run_drying)
    simulation_thread.daemon = True
    simulation_thread.start()
    return {"simulation_started": True}


def _run_individual_calendaring(electrode_type, parameters):
    """Run individual calendaring simulation."""
    if not electrode_type or electrode_type not in ["Anode", "Cathode"]:
        raise HTTPException(status_code=400, detail="electrode_type must be 'Anode' or 'Cathode' for calendaring")
    
    from simulation.process_parameters.Parameters import CalendaringParameters
    calendaring_params = CalendaringParameters(**parameters)
    calendaring_params.validate_parameters()
    
    def run_calendaring():
        try:
            from simulation.machine.CalendaringMachine import CalendaringMachine
            machine_id = f"{electrode_type.lower()}_calendaring_01"
            process_name = f"{electrode_type}_Calendaring"
            
            notify_machine_status(machine_id=machine_id, line_type="calendaring", process_name=process_name,
                                status="running", data={"message": f"Starting {electrode_type} calendaring", "parameters": parameters})
            
            calendaring_machine = CalendaringMachine(process_name=process_name, calendaring_parameters=calendaring_params)
            calendaring_machine.run()
            
            notify_machine_status(machine_id=machine_id, line_type="calendaring", process_name=process_name,
                                status="completed", data={"message": f"{electrode_type} calendaring completed", "results": calendaring_machine.get_current_state()})
        except Exception as e:
            notify_machine_status(machine_id=machine_id, line_type="calendaring", process_name=process_name,
                                status="error", data={"message": f"Calendaring failed: {str(e)}"})
    
    simulation_thread = threading.Thread(target=run_calendaring)
    simulation_thread.daemon = True
    simulation_thread.start()
    return {"simulation_started": True}


def _run_individual_slitting(electrode_type, parameters):
    """Run individual slitting simulation."""
    if not electrode_type or electrode_type not in ["Anode", "Cathode"]:
        raise HTTPException(status_code=400, detail="electrode_type must be 'Anode' or 'Cathode' for slitting")
    
    from simulation.process_parameters.Parameters import SlittingParameters
    slitting_params = SlittingParameters(**parameters)
    slitting_params.validate_parameters()
    
    def run_slitting():
        try:
            from simulation.machine.SlittingMachine import SlittingMachine
            machine_id = f"{electrode_type.lower()}_slitting_01"
            process_name = f"{electrode_type}_Slitting"
            
            notify_machine_status(machine_id=machine_id, line_type="slitting", process_name=process_name,
                                status="running", data={"message": f"Starting {electrode_type} slitting", "parameters": parameters})
            
            slitting_machine = SlittingMachine(process_name=process_name, slitting_parameters=slitting_params)
            slitting_machine.run()
            
            notify_machine_status(machine_id=machine_id, line_type="slitting", process_name=process_name,
                                status="completed", data={"message": f"{electrode_type} slitting completed", "results": slitting_machine.get_current_state()})
        except Exception as e:
            notify_machine_status(machine_id=machine_id, line_type="slitting", process_name=process_name,
                                status="error", data={"message": f"Slitting failed: {str(e)}"})
    
    simulation_thread = threading.Thread(target=run_slitting)
    simulation_thread.daemon = True
    simulation_thread.start()
    return {"simulation_started": True}


def _run_individual_inspection(electrode_type, parameters):
    """Run individual inspection simulation."""
    if not electrode_type or electrode_type not in ["Anode", "Cathode"]:
        raise HTTPException(status_code=400, detail="electrode_type must be 'Anode' or 'Cathode' for inspection")
    
    from simulation.process_parameters.Parameters import ElectrodeInspectionParameters
    inspection_params = ElectrodeInspectionParameters(**parameters)
    inspection_params.validate_parameters()
    
    def run_inspection():
        try:
            from simulation.machine.ElectrodeInspectionMachine import ElectrodeInspectionMachine
            machine_id = f"{electrode_type.lower()}_inspection_01"
            process_name = f"{electrode_type}_Inspection"
            
            notify_machine_status(machine_id=machine_id, line_type="inspection", process_name=process_name,
                                status="running", data={"message": f"Starting {electrode_type} inspection", "parameters": parameters})
            
            inspection_machine = ElectrodeInspectionMachine(process_name=process_name, electrode_inspection_parameters=inspection_params)
            inspection_machine.run()
            
            notify_machine_status(machine_id=machine_id, line_type="inspection", process_name=process_name,
                                status="completed", data={"message": f"{electrode_type} inspection completed", "results": inspection_machine.get_current_state()})
        except Exception as e:
            notify_machine_status(machine_id=machine_id, line_type="inspection", process_name=process_name,
                                status="error", data={"message": f"Inspection failed: {str(e)}"})
    
    simulation_thread = threading.Thread(target=run_inspection)
    simulation_thread.daemon = True
    simulation_thread.start()
    return {"simulation_started": True}


def _run_individual_rewinding(parameters):
    """Run individual rewinding simulation."""
    from simulation.process_parameters.Parameters import RewindingParameters
    rewinding_params = RewindingParameters(**parameters)
    rewinding_params.validate_parameters()
    
    def run_rewinding():
        try:
            from simulation.machine.RewindingMachine import RewindingMachine
            machine_id = "rewinding_01"
            process_name = "Rewinding"
            
            notify_machine_status(machine_id=machine_id, line_type="rewinding", process_name=process_name,
                                status="running", data={"message": "Starting rewinding", "parameters": parameters})
            
            rewinding_machine = RewindingMachine(process_name=process_name, rewinding_parameters=rewinding_params)
            rewinding_machine.run()
            
            notify_machine_status(machine_id=machine_id, line_type="rewinding", process_name=process_name,
                                status="completed", data={"message": "Rewinding completed", "results": rewinding_machine.get_current_state()})
        except Exception as e:
            notify_machine_status(machine_id=machine_id, line_type="rewinding", process_name=process_name,
                                status="error", data={"message": f"Rewinding failed: {str(e)}"})
    
    simulation_thread = threading.Thread(target=run_rewinding)
    simulation_thread.daemon = True
    simulation_thread.start()
    return {"simulation_started": True}


def _run_individual_electrolyte_filling(parameters):
    """Run individual electrolyte filling simulation."""
    from simulation.process_parameters.Parameters import ElectrolyteFillingParameters
    filling_params = ElectrolyteFillingParameters(**parameters)
    filling_params.validate_parameters()
    
    def run_filling():
        try:
            from simulation.machine.ElectrolyteFillingMachine import ElectrolyteFillingMachine
            machine_id = "electrolyte_filling_01"
            process_name = "Electrolyte_Filling"
            
            notify_machine_status(machine_id=machine_id, line_type="electrolyte_filling", process_name=process_name,
                                status="running", data={"message": "Starting electrolyte filling", "parameters": parameters})
            
            filling_machine = ElectrolyteFillingMachine(process_name=process_name, electrolyte_filling_parameters=filling_params)
            filling_machine.run()
            
            notify_machine_status(machine_id=machine_id, line_type="electrolyte_filling", process_name=process_name,
                                status="completed", data={"message": "Electrolyte filling completed", "results": filling_machine.get_current_state()})
        except Exception as e:
            notify_machine_status(machine_id=machine_id, line_type="electrolyte_filling", process_name=process_name,
                                status="error", data={"message": f"Electrolyte filling failed: {str(e)}"})
    
    simulation_thread = threading.Thread(target=run_filling)
    simulation_thread.daemon = True
    simulation_thread.start()
    return {"simulation_started": True}


def _run_individual_formation_cycling(parameters):
    """Run individual formation cycling simulation."""
    from simulation.process_parameters.Parameters import FormationCyclingParameters
    formation_params = FormationCyclingParameters(**parameters)
    formation_params.validate_parameters()
    
    def run_formation():
        try:
            from simulation.machine.FormationCyclingMachine import FormationCyclingMachine
            machine_id = "formation_cycling_01"
            process_name = "Formation_Cycling"
            
            notify_machine_status(machine_id=machine_id, line_type="formation_cycling", process_name=process_name,
                                status="running", data={"message": "Starting formation cycling", "parameters": parameters})
            
            formation_machine = FormationCyclingMachine(process_name=process_name, formation_cycling_parameters=formation_params)
            formation_machine.run()
            
            notify_machine_status(machine_id=machine_id, line_type="formation_cycling", process_name=process_name,
                                status="completed", data={"message": "Formation cycling completed", "results": formation_machine.get_current_state()})
        except Exception as e:
            notify_machine_status(machine_id=machine_id, line_type="formation_cycling", process_name=process_name,
                                status="error", data={"message": f"Formation cycling failed: {str(e)}"})
    
    simulation_thread = threading.Thread(target=run_formation)
    simulation_thread.daemon = True
    simulation_thread.start()
    return {"simulation_started": True}


def _run_individual_aging(parameters):
    """Run individual aging simulation."""
    from simulation.process_parameters.Parameters import AgingParameters
    aging_params = AgingParameters(**parameters)
    aging_params.validate_parameters()
    
    def run_aging():
        try:
            from simulation.machine.AgingMachine import AgingMachine
            machine_id = "aging_01"
            process_name = "Aging"
            
            notify_machine_status(machine_id=machine_id, line_type="aging", process_name=process_name,
                                status="running", data={"message": "Starting aging", "parameters": parameters})
            
            aging_machine = AgingMachine(process_name=process_name, aging_parameters=aging_params)
            aging_machine.run()
            
            notify_machine_status(machine_id=machine_id, line_type="aging", process_name=process_name,
                                status="completed", data={"message": "Aging completed", "results": aging_machine.get_current_state()})
        except Exception as e:
            notify_machine_status(machine_id=machine_id, line_type="aging", process_name=process_name,
                                status="error", data={"message": f"Aging failed: {str(e)}"})
    
    simulation_thread = threading.Thread(target=run_aging)
    simulation_thread.daemon = True
    simulation_thread.start()
    return {"simulation_started": True}


@app.post("/api/simulation/mixing/start")
def start_mixing_simulation(mixing_data: dict):
    """Start real mixing simulation using actual MixingMachine class."""
    try:
        electrode_type = mixing_data.get("electrode_type")
        if not electrode_type or electrode_type not in ["Anode", "Cathode"]:
            raise HTTPException(status_code=400, detail="Invalid electrode_type. Must be 'Anode' or 'Cathode'")
        
        # Validate input ratios
        required_fields = ["PVDF", "CA", "AM", "Solvent"]
        for field in required_fields:
            if field not in mixing_data:
                raise HTTPException(status_code=400, detail=f"Missing required field: {field}")
        
        # Check if ratios sum to 1.0
        total = sum(mixing_data[field] for field in required_fields)
        if abs(total - 1.0) > 0.0001:
            raise HTTPException(status_code=400, detail=f"Ratios must sum to 1.0, got {total}")
        
        # Start real mixing simulation in a separate thread
        def run_real_mixing_simulation():
            try:
                from simulation.machine.MixingMachine import MixingMachine
                from simulation.battery_model.MixingModel import MixingModel
                from simulation.process_parameters.MixingParameters import MixingParameters, MaterialRatios
                
                machine_id = f"{electrode_type.lower()}_mixing_01"
                process_name = f"{electrode_type}_Mixing"
                
                print(f" STARTING REAL {electrode_type} MIXING SIMULATION")
                print(f" Machine ID: {machine_id}")
                print(f" Parameters: {mixing_data}")
                
                # Notify simulation start
                notify_machine_status(
                    machine_id=machine_id,
                    line_type="mixing",
                    process_name=process_name,
                    status="running",
                    data={
                        "message": f"Starting {electrode_type} mixing simulation",
                        "parameters": mixing_data
                    }
                )
                
                # Create the real simulation objects
                mixing_model = MixingModel(electrode_type)
                
                # Create MaterialRatios from input data
                material_ratios = MaterialRatios(
                    AM=mixing_data["AM"],
                    CA=mixing_data["CA"],
                    PVDF=mixing_data["PVDF"],
                    solvent=mixing_data["Solvent"]
                )
                
                mixing_parameters = MixingParameters(material_ratios=material_ratios)
                
                # Create and configure the mixing machine
                mixing_machine = MixingMachine(
                    process_name=process_name,
                    mixing_model=mixing_model,
                    mixing_parameters=mixing_parameters
                )
                
                # Set the battery model
                mixing_machine.receive_model_from_previous_process(mixing_model)
                
                print(f"  Running {electrode_type} mixing simulation...")
                
                # Run the actual simulation
                mixing_machine.run()
                
                print(f" {electrode_type} MIXING SIMULATION COMPLETED")
                
                # Get final results from the simulation
                final_state = mixing_machine.get_current_state()
                
                # Notify completion with real results
                notify_machine_status(
                    machine_id=machine_id,
                    line_type="mixing",
                    process_name=process_name,
                    status="completed",
                    data={
                        "message": f"{electrode_type} mixing simulation completed successfully",
                        "results": final_state
                    }
                )
                
            except Exception as e:
                print(f"❌ ERROR in {electrode_type} mixing simulation: {str(e)}")
                import traceback
                traceback.print_exc()
                # Notify error
                notify_machine_status(
                    machine_id=machine_id,
                    line_type="mixing", 
                    process_name=process_name,
                    status="error",
                    data={"message": f"Mixing simulation failed: {str(e)}"}
                )
        
        # Start real simulation in background thread
        simulation_thread = threading.Thread(target=run_real_mixing_simulation)
        simulation_thread.daemon = True
        simulation_thread.start()
        
        return {
            "message": f"{electrode_type} mixing simulation started successfully",
            "electrode_type": electrode_type,
            "parameters": mixing_data
        }
        
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
