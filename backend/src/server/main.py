from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from simulation.factory.Factory import Factory
from simulation.battery_model.Slurry import Slurry
from simulation.machine.MixingMachine import MixingMachine
from simulation.machine.CoatingMachine import CoatingMachine
from pathlib import Path
from zipfile import ZipFile
import json
import shutil

app = FastAPI()

# Allow frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

RESULTS_PATH = Path("results")
RESULTS_PATH.mkdir(parents=True, exist_ok=True)

class SlurryInput(BaseModel):
    PVDF: float
    CA: float
    AM: float
    Solvent: float
    electrode_type: str

class DualInput(BaseModel):
    anode: SlurryInput
    cathode: SlurryInput

factory = Factory()
machines = {}

@app.post("/start-both")
def start_both_simulation(payload: DualInput):
    try:
        # Reset factory and clear any existing machines
        factory.stop_simulation()
        factory.machines = []
        factory.threads = []
        factory.machine_status = {}
        factory.machine_locks = {}
        factory.machine_events = {}
        #Create mixing machines
        for data in [payload.anode, payload.cathode]:
            slurry = Slurry(data.electrode_type)
            ratios = {
                "PVDF": data.PVDF,
                "CA": data.CA,
                "AM": data.AM,
                "H2O" if data.electrode_type == "Anode" else "NMP": data.Solvent
            }

            machine_id = f"TK_Mix_{data.electrode_type}"
            mixing_machine = MixingMachine(machine_id, data.electrode_type, slurry, ratios)
            factory.add_machine(mixing_machine)
            machines[data.electrode_type] = mixing_machine

        # Create and add coating machine with dependencies
        coating_machine = CoatingMachine("Coating_Machine")
        factory.add_machine(coating_machine, dependencies=["TK_Mix_Anode", "TK_Mix_Cathode"])
        machines["Coating"] = coating_machine

        # Start simulation for all machines
        factory.start_simulation()

        # Wait for all machines to complete
        for thread in factory.threads:
            thread.join()

        # Check if all machines completed successfully
        all_completed = all(factory.machine_status.values())
        if not all_completed:
            raise Exception("Not all machines completed successfully")

        # Save final results
        for data in [payload.anode, payload.cathode]:
            machine = machines[data.electrode_type]
            final_result = machine._format_result(is_final=True)
            result_path = RESULTS_PATH / f"{data.electrode_type}_result.json"
            with open(result_path, "w") as f:
                json.dump(final_result, f, indent=4)

        # Get completion status for each machine
        completion_status = {
            machine_id: {
                "completed": status,
                "timestamp": machines[data.electrode_type]._format_result(is_final=True)["TimeStamp"] if machine_id != "Coating_Machine" else "N/A"
            }
            for machine_id, status in factory.machine_status.items()
        }

        return {
            "message": "All processes completed successfully.",
            "completion_status": completion_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
def reset_simulation():
    try:
        shutil.rmtree(RESULTS_PATH)
        RESULTS_PATH.mkdir()
        factory.reset()
        machines.clear()
        return {"message": "Factory and data reset."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/{electrode_type}")
def download_result_zip(electrode_type: str):
    try:
        '''
        json_file = RESULTS_PATH / f"{electrode_type}_result.json"
        if not json_file.exists():
            raise FileNotFoundError(f"No result file for {electrode_type}")
        
        zip_path = RESULTS_PATH / f"{electrode_type}.zip"
        with ZipFile(zip_path, "w") as zipf:
            zipf.write(json_file, arcname=json_file.name)
        '''
        zip_path = RESULTS_PATH / f"{electrode_type}.zip"

        with ZipFile(zip_path, "w") as zipf:
            for file in (Path.cwd() / "mixing_output").glob(f"*{electrode_type}*.json"):
                zipf.write(file, arcname=file.name)

        return FileResponse(zip_path, media_type='application/zip', filename=f"{electrode_type}.zip")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    

    
#this one is not included yet, we can put this if it's needed later
'''
@app.get("/files/all")
def download_all_results():
    try:
        zip_path = RESULTS_PATH / "all_results.zip"

        # Check for any .json files to include
        json_files = list(RESULTS_PATH.glob("*.json"))
        if not json_files:
            raise FileNotFoundError("No result file for all")

        with ZipFile(zip_path, "w") as zipf:
            for file in json_files:
                zipf.write(file, arcname=file.name)

        return FileResponse(zip_path, media_type='application/zip', filename="all_results.zip")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
'''