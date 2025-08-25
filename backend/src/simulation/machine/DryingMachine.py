import json
import time
import os
from datetime import datetime, timedelta
from simulation.machine.BaseMachine import BaseMachine
from simulation.sensor.DryingPropertyCalculator import DryingPropertyCalculator
import threading

class DryingMachine(BaseMachine):
    """
    Simulates the drying process in battery manufacturing.
    Removes solvent from the coated electrode to form a dry film.
    """

    def __init__(self, id, web_speed):
        super().__init__(id)
        self.name = "DryingMachine"
        self.start_datetime = datetime.now()
        self.total_time = 0
        self.lock = threading.Lock()
        # Create output directory
        self.output_dir = os.path.join(os.getcwd(), "drying_output")
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory created at: {self.output_dir}")

        # Parameters from coating
        self.wet_thickness = 0
        self.solid_content = 0
        self.web_speed = web_speed

        # Initialize calculator
        self.calculator = DryingPropertyCalculator()
    def _format_result(self, evap_rate, delta_coat, defect_risk, is_final=False):
        """
        Format the current or final process data as a dictionary.
        """
        with self.lock:
            base = {
                "TimeStamp": (self.start_datetime + timedelta(seconds=self.total_time)).isoformat(),
                "Duration": round(self.total_time, 5),
                "Machine ID": self.id,
                "Process": "Drying"
            }

            properties = {
                "Wet Thickness (m)": round(self.wet_thickness, 6),
                "Dry Thickness (m)": round(self.dry_thickness, 6),
                "Remaining Solvent (kg/m²)": round(self.M_solvent, 6),
                "Evaporation Rate (kg/s)": round(evap_rate, 6),
                "Current Coating Thickness (m)": round(delta_coat, 6),
                "Defect Risk": defect_risk
            }

            if is_final:
                base["Final Properties"] = properties
            else:
                base.update(properties)

            return base

    def _write_json(self, data, filename):
        """
        Write the result dictionary to a JSON file.
        """
        try:
            timestamp = data["TimeStamp"].replace(":", "-").replace(".", "-")
            unique_filename = f"{self.output_dir}/{self.id}_{timestamp}_{filename}"
            
            with open(unique_filename, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Results saved to {unique_filename}")
        except Exception as e:
            print(f"Error writing result to file: {e}")

    def _simulate(self, end_time=100):
        """
        Internal simulation loop for drying.
        Generates JSON files at each iteration step.
        """
        last_saved_time = time.time()
        last_saved_result = None
        for t in range(0, self.calculator.time_steps(self.web_speed) + 1):
            self.total_time = t
            evap_rate = self.calculator.evaporation_rate()
            self.M_solvent -= (evap_rate / self.calculator.area()) * self.calculator.delta_t
            self.M_solvent = max(self.M_solvent, 0)
            delta_coat = self.dry_thickness + (self.M_solvent / self.calculator.solvent_density)
            defect_risk = abs(evap_rate / self.calculator.area()) > self.calculator.max_safe_evap_rate

            result = self._format_result(evap_rate, delta_coat, defect_risk)
            
            # Save results periodically, but only if data has changed
            now = time.time()
            if now - last_saved_time >= 0.1 and result != last_saved_result:  # Check if data has changed
                filename = f"result_at_{round(self.total_time)}s.json"
                self._write_json(result, filename)
                last_saved_time = now
                last_saved_result = result

            # Optional delay to simulate real-time progression
            time.sleep(0.1)
            
            if self.M_solvent == 0:
                break 


    def run(self):
        """
        Run the drying simulation.
        """
        if self.is_on:
            self._simulate()

            # Recalculate final values
            evap_rate = self.calculator.evaporation_rate()
            delta_coat = self.dry_thickness + (self.M_solvent / self.calculator.solvent_density)
            defect_risk = abs(evap_rate / self.calculator.area()) > self.calculator.max_safe_evap_rate

            print(f"Drying process completed on {self.id}\n")

    def update_from_coating(self, wet_thickness_coating, solid_content_coating):
        with self.lock:
            self.wet_thickness, self.solid_content = wet_thickness_coating, solid_content_coating
            print(f"[{self.id}] Received from coating - wet_thickness={self.wet_thickness}, solid_content={self.solid_content}")

            # Recalculate based on updated inputs
            self.dry_thickness = self.calculator.calculate_dry_thickness(self.wet_thickness, self.solid_content)
            print(f"[DEBUG] dry_thickness={self.dry_thickness}")
            self.M_solvent = self.calculator.calculate_initial_solvent_mass(self.wet_thickness, self.solid_content)
            
    def get_final_drying(self):
        with self.lock:
            dry_thickness_drying = self.dry_thickness  # just use the float
            return dry_thickness_drying