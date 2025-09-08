from fastapi import FastAPI
from simulation.factory.PlantSimulation import PlantSimulation
import uvicorn


app = FastAPI()
battery_plant_simulation = PlantSimulation()


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/machine/:machine_id/status")
def get_machine_status(machine_id: str):
    return {"message": f"Machine {machine_id} is running"}

@app.post("/machine/:machine_id/parameters")
def update_machine_params(machine_id: str):
    return {"message": f"Machine {machine_id} is running"}

@app.post("/factory/start")
def start_factory():
    return {"message": "Factory is starting"}

@app.get("/factory/logs/current")
def get_factory_logs():
    return {"message": "Factory logs"}
    
@app.get("/factory/logs/all")
def get_factory_logs_all():
    return {"message": "Factory logs all"}

@app.websocket("/factory/logs/stream")
async def get_factory_logs_stream():
    return {"message": "Factory logs stream"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
