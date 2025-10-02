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
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            # Remove disconnected websocket
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)

manager = ConnectionManager()


@app.get("/")
def root():
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


@app.post("/api/simulation/start")
def start_full_simulation(simulation_data: dict):
    """Start full simulation with anode and cathode mixing parameters."""
    global battery_plant_simulation
    global factory_run_thread
    global out_of_batch_event
    
    try:
        # Extract anode and cathode parameters from the input
        anode_params = simulation_data.get("anode_params")
        cathode_params = simulation_data.get("cathode_params")
        
        if not anode_params or not cathode_params:
            raise HTTPException(
                status_code=400, 
                detail="Both anode_params and cathode_params are required"
            )
        
        # Validate required fields for both electrode types
        required_fields = ["PVDF", "CA", "AM", "Solvent"]
        
        for field in required_fields:
            if field not in anode_params:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Missing required anode field: {field}"
                )
            if field not in cathode_params:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Missing required cathode field: {field}"
                )
        
        # Check if ratios sum to 1.0 for anode
        anode_total = sum(anode_params[field] for field in required_fields)
        if abs(anode_total - 1.0) > 0.0001:
            raise HTTPException(
                status_code=400, 
                detail=f"Anode ratios must sum to 1.0, got {anode_total}"
            )
        
        # Check if ratios sum to 1.0 for cathode
        cathode_total = sum(cathode_params[field] for field in required_fields)
        if abs(cathode_total - 1.0) > 0.0001:
            raise HTTPException(
                status_code=400, 
                detail=f"Cathode ratios must sum to 1.0, got {cathode_total}"
            )
        
        # Create batch with the provided parameters
        batch = Batch(
            batch_id=str(uuid.uuid4()),
            anode_mixing_params=anode_params,
            cathode_mixing_params=cathode_params
        )
        
        # Add batch to simulation
        battery_plant_simulation.add_batch(batch)
        
        # Start or restart factory simulation thread
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
        
        return {
            "message": "Full simulation started successfully",
            "batch_id": batch.batch_id,
            "anode_params": anode_params,
            "cathode_params": cathode_params
        }
        
    except ValueError as e:
        # over limit of batches or other validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


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


# Background task to process notifications and broadcast to WebSocket clients
async def process_notifications():
    """Background task to process machine notifications and broadcast to WebSocket clients."""
    while True:
        try:
            # Get notification from queue
            notification = await notification_queue.get_notification()
            
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
