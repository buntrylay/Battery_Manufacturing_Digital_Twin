from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from simulation.factory.Factory import Factory
from simulation.battery_model.Slurry import Slurry
from simulation.machine.MixingMachine import MixingMachine
from simulation.machine.CoatingMachine import CoatingMachine
from simulation.machine.DryingMachine import DryingMachine
from simulation.machine.CalendaringMachine import CalendaringMachine
from simulation.machine.SlittingMachine import SlittingMachine
from simulation.machine.ElectrodeInspectionMachine import ElectrodeInspectionMachine
from simulation.machine.RewindingMachine import RewindingMachine
from pathlib import Path
from zipfile import ZipFile
import json
import shutil
from glob import glob
import time

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
        factory.stop_simulation()
        factory.machines = []
        factory.threads = []
        factory.machine_status = {}
        factory.machine_locks = {}
        factory.machine_events = {}

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

        user_input_coating = {
            "coating_speed": 0.05,
            "gap_height": 200e-6,
            "flow_rate": 5e-6,
            "coating_width": 0.5
        }

        anode_coating_machine = CoatingMachine("MC_Coat_Anode", user_input_coating)
        cathode_coating_machine = CoatingMachine("MC_Coat_Cathode", user_input_coating)

        factory.add_machine(anode_coating_machine, dependencies=["TK_Mix_Anode"])
        factory.add_machine(cathode_coating_machine, dependencies=["TK_Mix_Cathode"])

        machines["Anode_Coating"] = anode_coating_machine
        machines["Cathode_Coating"] = cathode_coating_machine

        # Add Drying machines
        for etype in ["Anode", "Cathode"]:
            drying_id = f"MC_Dry_{etype}"
            coat_id = f"MC_Coat_{etype}"
            drying_machine = DryingMachine(drying_id, web_speed=0.5)
            factory.add_machine(drying_machine, dependencies=[coat_id])
            machines[f"{etype}_Drying"] = drying_machine
            
        # Add Calendaring machines
        user_input_calendaring = {
            "roll_gap": 100e-6,             # meters
            "roll_pressure": 2e6,           # Pascals
            "roll_speed": 2.0,              # m/s
            "dry_thickness": 150e-6,        # From coating (m)
            "initial_porosity": 0.45,       # Assumed porosity after drying
            "temperature": 25               # Optional
        }
        for etype in ["Anode", "Cathode"]:
            calendaring_id = f"MC_Cal_{etype}"
            drying_id = f"MC_Dry_{etype}"
            calendaring_machine = CalendaringMachine(calendaring_id, user_input_calendaring)
            factory.add_machine(calendaring_machine, dependencies=[drying_id])
            machines[f"{etype}_Calendaring"] = calendaring_machine
            
        # Add Slitting machines
        user_input_slitting = {
            "w_input": 500,
            "blade_sharpness": 8,
            "slitting_speed": 1.5, 
            "target_width": 100,
            "slitting_tension": 150,
        }
        for etype in ["Anode", "Cathode"]:
            slitting_id = f"MC_Slit_{etype}"
            calendaring_id = f"MC_Cal_{etype}"
            slitting_machine = SlittingMachine(slitting_id, user_input_slitting)
            factory.add_machine(slitting_machine, dependencies=[calendaring_id])
            machines[f"{etype}_Slitting"] = slitting_machine
        
        # Add Electrode Inspection machines
        user_input_electrode_inspection = {
            "epsilon_width_max": 0.1,  
            "epsilon_thickness_max": 10e-6,
            "B_max": 2.0,
            "D_surface_max": 3
        }
        for etype in ["Anode", "Cathode"]:
            inspection_id = f"MC_Inspect_{etype}"
            slitting_id = f"MC_Slit_{etype}"
            inspection_machine = ElectrodeInspectionMachine(inspection_id, user_input_electrode_inspection)
            factory.add_machine(inspection_machine, dependencies=[slitting_id])
            machines[f"{etype}_Inspection"] = inspection_machine
        
           
        user_input_rewinding = {
            "rewinding_speed": 0.5,  # m/s
            "initial_tension": 100,       # N
            "tapering_steps": 0.3, # meters
            "environment_humidity": 30    # %
        }
        
        for etype in ["Anode", "Cathode"]:
            rewinding_id = f"MC_Rewind_{etype}"
            inspection_id = f"MC_Inspect_{etype}"
            rewinding_machine = RewindingMachine(rewinding_id, user_input_rewinding)
            factory.add_machine(rewinding_machine, dependencies=[inspection_id])
            machines[f"{etype}_Rewinding"] = rewinding_machine

        factory.start_simulation()

        for thread in factory.threads:
            thread.join()

        all_completed = all(factory.machine_status.values())
        if not all_completed:
            raise Exception("Not all machines completed successfully")

        for data in [payload.anode, payload.cathode]:
            machine = machines[data.electrode_type]
            final_result = machine._format_result(is_final=True)
            result_path = RESULTS_PATH / f"{data.electrode_type}_result.json"
            with open(result_path, "w") as f:
                json.dump(final_result, f, indent=4)

        completion_status = {
            machine_id: {
                "completed": status,
                "timestamp": machines[data.electrode_type]._format_result(is_final=True)["TimeStamp"]
                if machine_id != "Coating_Machine" else "N/A"
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
            for file in (Path.cwd() / "simulation_output").glob(f"*{electrode_type}*.json"):
                zipf.write(file, arcname=file.name)

        return FileResponse(zip_path, media_type='application/zip', filename=f"{electrode_type}.zip")
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
    
'''
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

        # Define the coating parameters
        user_input_coating = {
            "coating_speed": 0.05,  # m/s (0,05 - 5 m/s)
            "gap_height": 200e-6, # meters (50e-6 to 300 e-6)
            "flow_rate": 5e-6,  # m³/s (Possibly fixed)
            "coating_width": 0.5  # m (possibly fixed)
        }

        # Create coating machine instances
        anode_coating_machine = CoatingMachine("MC_Coat_Anode", user_input_coating)
        cathode_coating_machine = CoatingMachine("MC_Coat_Cathode", user_input_coating)

        factory.add_machine(anode_coating_machine, 
                   dependencies=["TK_Mix_Anode"])  # Depends on anode mixer
        print("Anode coating machine added")
        factory.add_machine(cathode_coating_machine, 
                   dependencies=["TK_Mix_Cathode"])  # Depends on cathode mixer
        print("Cathode coating machine added")
        
        machines["Anode_Coating"] = anode_coating_machine
        machines["Cathode_Coating"] = cathode_coating_machine

        # Start simulation for all machines
        factory.start_simulation()

        # Wait for all machines to complete
        for thread in factory.threads:
            thread.join()

        # Check if all machines completed successfully
        all_completed = all(factory.machine_status.values())
        if not all_completed:
            raise Exception("Not all machines completed successfully")

         # >>> ADDED: Drying stage 
        for etype in ["Anode", "Cathode"]:
            coat_id = f"MC_Coat_{etype}"
            max_wait_time = 10  # seconds
            waited = 0
            coating_result_path = None
            while waited < max_wait_time:
                matching_files = sorted(glob(f"coating_output/*final_results_{coat_id}.json"), reverse=True)
                if matching_files:
                    coating_result_path = matching_files[0]
                    break
                time.sleep(0.5)
                waited += 0.5

            if not coating_result_path:
                raise FileNotFoundError(f"No final coating result found for {coat_id} after waiting {max_wait_time} seconds.")

            with open(coating_result_path) as f:
                coating_data = json.load(f)

            props = coating_data["Final Properties"]
            wet_thickness = props["wet_thickness_m"]
            solid_content = props["solid_content"]

            drying_machine = DryingMachine(f"MC_Dry_{etype}", wet_thickness, solid_content, web_speed=0.5)
            drying_machine.run()
        # <<< END Drying stage        
       
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
'''

    
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