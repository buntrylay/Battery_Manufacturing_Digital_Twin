from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from Slurry import Slurry
from Machines import MixingMachine
from Factory import Factory
from pathlib import Path
import shutil
import zipfile
import os

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for cross-origin frontend communication (e.g., React at localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the absolute path to the results directory
BASE_DIR = Path("C:/Users/13min/factory-ui")
RESULTS_DIR = BASE_DIR / "Sprint_1_SlurryMixing" / "MixingProcess" / "results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)  # Ensure results directory exists

# Input data model for slurry mixing request
class SlurryInput(BaseModel):
    PVDF: float
    CA: float
    AM: float
    Solvent: float
    electrode_type: str

# Endpoint to start the simulation for anode or cathode slurry
@app.post("/start")
def start_simulation(data: SlurryInput):
    try:
        slurry = Slurry(data.electrode_type)
        ratios = {
            "PVDF": data.PVDF,
            "CA": data.CA,
            "AM": data.AM,
            "H2O" if data.electrode_type == "Anode" else "NMP": data.Solvent
        }

        factory = Factory()
        machine_id = f"Mix_{data.electrode_type}"
        machine = MixingMachine(machine_id, data.electrode_type, slurry, ratios)
        factory.add_machine(machine)
        factory.start_simulation()

        return {"status": "success", "message": f"{data.electrode_type} mixing simulation completed."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to reset the simulation by clearing all result files
@app.post("/reset")
def reset_simulation():
    try:
        if RESULTS_DIR.exists():
            shutil.rmtree(RESULTS_DIR)  # Delete the results directory
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)  # Recreate the directory
        return {"status": "success", "message": "Simulation data reset and JSON files deleted."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to download all result .json files as a zip
@app.get("/files")
def download_results():
    zip_path = RESULTS_DIR.parent / "results_bundle.zip"

    # Create a zip archive of all result JSON files
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for file in RESULTS_DIR.glob("*.json"):
            zipf.write(file, arcname=file.name)

    # Return the zipped file as a downloadable response
    return FileResponse(
        path=zip_path,
        filename="results_bundle.zip",
        media_type="application/zip"
    )
