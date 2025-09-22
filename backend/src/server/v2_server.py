import os
import sys
import threading
from fastapi import FastAPI, HTTPException
import uvicorn

# --- Path and Simulation Module Imports ---
# This points from `backend/src/server` up one level to `backend/src` so that `simulation` can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the core simulation class
from simulation.factory.PlantSimulation import PlantSimulation

app = FastAPI()
battery_plant_simulation = PlantSimulation()
factory_run_thread = threading.Thread(target=battery_plant_simulation.run_pipeline)


@app.get("/")
def root():
    return {"message": "This is the V2 API for the battery manufacturing digital twin!"}


@app.get("/plant/state")
def get_plant_state():
    """Get the current state of the plant. Returns a dictionary with the current state of the plant."""
    # quite done, just some validation I think depending on my teammate's implementation of get_current_plant_state()
    return battery_plant_simulation.get_current_plant_state()


@app.get("/machine/{line_type}/{machine_id}/status")
def get_machine_status(line_type: str, machine_id: str):
    """Get the status of a machine. Returns a dictionary with the status of the machine."""
    # quite done, just some validation I think depending on my teammate's implementation of get_machine_status()
    return battery_plant_simulation.get_machine_status(line_type, machine_id)


@app.patch("/machine/{line_type}/{machine_id}/parameters")
def update_machine_params(line_type: str, machine_id: str, parameters: dict):
    """Update machine parameters with validation."""
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


@app.post("/factory/start")
def start_factory(batch: dict):
    battery_plant_simulation.add_batch(batch)
    if not factory_run_thread.is_alive():
        factory_run_thread.start()
    return {"message": "Batch added successfully"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
