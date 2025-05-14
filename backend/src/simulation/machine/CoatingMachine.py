from simulation.machine.BaseMachine import BaseMachine
from simulation.sensor.CoatingPropertyCalculator import CoatingPropertyCalculator
import time
from datetime import datetime, timedelta
import json
import os
import random
import threading

class CoatingMachine(BaseMachine):
    """
    A coating machine that simulates the electrode coating process.
    
    This class handles the coating process for battery electrodes, including:
    - Multiple coating steps
    - Process parameter simulation
    - Quality metrics calculation
    - Real-time data logging
    """
    
    def __init__(self, id, machine_parameters: dict):
        """
        Initialize the coating machine.
        
        Args:
            id (str): Unique identifier for the machine
        """
        super().__init__(id)
        self.start_datetime = datetime.now()
        self.total_time = 0
        self.lock = threading.Lock()

        # Create simulation_output directory in the current working directory
        self.output_dir = os.path.join(os.getcwd(), "coating_output")
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory created at: {self.output_dir}")
        
        # Initialise calculator and process parameters
        self.calculator = CoatingPropertyCalculator()
        
        # Input parameters
        self.coating_speed = machine_parameters["coating_speed"]  # m/s (0,05 - 5 m/s)
        self.gap_height = machine_parameters["gap_height"] # meters (50e-6 to 300 e-6)
        self.flow_rate = machine_parameters["flow_rate"]  # m³/s (Possibly fixed)
        self.coating_width = machine_parameters["coating_width"] # m (possibly fixed)
        
        # Variables from Mixing
        self.viscosity_pa = 0
        self.solid_content = 0  # fraction (e.g., 0.55 for 55%)

    def _format_result(self, step=None, is_final=False):
        """
        Format the current or final process data as a dictionary.
        """
        with self.lock:
            base = {
                "TimeStamp": (self.start_datetime + timedelta(seconds=self.total_time)).isoformat(),
                "Duration": round(self.total_time, 5),
                "Machine ID": self.id,
                "Process": "Coating"
            }
            
            properties = {
                "shear_rate_1_per_s": round(self.shear_rate, 4),
                "viscosity_Pa_s": round(self.viscosity_pa, 4),
                "wet_thickness_m": round(self.wet_thickness, 5),
                "dry_thickness_m": round(self.dry_thickness, 5),
                "defect_risk": self.defect_risk,
                "uniformity_std": round(self.uniformity_std, 4)
            }
            
            if is_final:
                base["Final Properties"] = properties
            else:
                base.update(properties)

            return base

    def _write_json(self, data, filename):
        """
        Write a dictionary to a JSON file.
        """
        try:
            timestamp = data["TimeStamp"].replace(":", "-").replace(".", "-")
            unique_filename = f"coating_output/{self.id}_{timestamp}_{filename}"
            
            with open(unique_filename, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Results saved to {unique_filename}")
        except Exception as e:
            print(f"Error writing result to file: {e}")

    def _simulate(self, end_time=100):
        """
        Simulate a single coating step with process parameters and quality metrics.
        
        Args:
            step (int): Current step number
        """
        last_saved_time = time.time()
        last_saved_result = None

        for t in range(0, end_time+1, 5):
            self.total_time = t
            self.shear_rate = self.calculator.calculate_shear_rate(self.coating_speed, self.gap_height)
            self.wet_thickness = self.calculator.calculate_wet_thickness(self.flow_rate, self.coating_speed, self.coating_width)
            self.dry_thickness = self.calculator.calculate_dry_thickness(self.wet_thickness, self.solid_content)
            self.defect_risk = self.calculator.check_defect_risk(self.coating_speed, self.gap_height, self.viscosity_pa)
            self.uniformity_std = self.calculator.calculate_uniformity(self.shear_rate)

            result = self._format_result()

             # Save results periodically, but only if data has changed
            now = time.time()
            if now - last_saved_time >= 0.1 and result != last_saved_result:  # Check if data has changed
                filename = f"result_at_{round(self.total_time)}s.json"
                self._write_json(result, filename)
                last_saved_time = now
                last_saved_result = result
            
            time.sleep(0.1)


    def run(self):
        """
        Run the coating process with detailed step simulation.
        """
        if self.is_on:
            self._simulate()
            
            # Save final results
            final_result = self._format_result(is_final=True)
            filename = f"final_results_{self.id}.json"
            self._write_json(final_result, filename)
            
            print(f"Coating process completed on {self.id}\n")

    def update_from_slurry(self, slurry):
        """
        Update coating machine properties from a slurry object.
        
        Args:
            slurry (Slurry): The slurry object from the mixing machine
        """
        with self.lock:
            # Calculate total volume of solids
            total_solids = slurry.AM + slurry.CA + slurry.PVDF
            total_volume = total_solids + getattr(slurry, slurry.solvent)
            self.solid_content = total_solids / total_volume if total_volume > 0 else 0
            
            # Get viscosity from the slurry's calculator
            self.viscosity_pa = slurry.viscosity
            
            print(f"Updated {self.id} with properties from slurry")
            print(f"Viscosity: {self.viscosity_pa:.2f} Pa·s, Solid Content: {self.solid_content:.2%}") 