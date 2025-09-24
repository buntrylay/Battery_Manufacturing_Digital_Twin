import os
import sys

# for simulation & concurrency
import threading

# for API
from fastapi import FastAPI, HTTPException
import uvicorn

# for generation of unique batch ID
import uuid

# --- Path and Simulation Module Imports ---
# This points from `backend/src/server` up one level to `backend/src` so that `simulation` can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the core simulation class
from simulation.factory.Batch import Batch
from simulation.factory.PlantSimulation import PlantSimulation

app = FastAPI()
battery_plant_simulation = PlantSimulation()
factory_run_thread = None
out_of_batch_event = threading.Event()


@app.get("/")
def root():
    return {"message": "This is the V2 API for the battery manufacturing digital twin!"}


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



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
