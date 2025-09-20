import threading
from fastapi import FastAPI, HTTPException
from simulation.factory.PlantSimulation import PlantSimulation
import uvicorn


app = FastAPI()
battery_plant_simulation = PlantSimulation()
factory_run_thread = threading.Thread(target=battery_plant_simulation.run_pipeline)


@app.get("/")
def root():
    return {"message": "This is the V2 API for the battery manufacturing digital twin!"}


@app.get("/plant/state")
def get_plant_state():
    return battery_plant_simulation.get_current_plant_state()


@app.get("/machine/{line_type}/{machine_id}/status")
def get_machine_status(line_type: str, machine_id: str):
    return battery_plant_simulation.get_machine_status(line_type, machine_id)


@app.patch("/machine/{line_type}/{machine_id}/parameters")
def update_machine_params(line_type: str, machine_id: str, parameters: dict):
    """Update machine parameters with validation."""
    try:
        battery_plant_simulation.update_machine_parameters(
            line_type, machine_id, parameters
        )
        return {
            "message": f"Machine {machine_id} parameters updated successfully",
            "line_type": line_type,
            "machine_id": machine_id,
        }
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


@app.get("/factory/logs")
def get_factory_logs_all():
    return {"message": "Factory logs"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
