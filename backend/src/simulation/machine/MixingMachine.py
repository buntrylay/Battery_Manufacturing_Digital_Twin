import time
from datetime import datetime, timedelta
from simulation.machine.BaseMachine import BaseMachine
from simulation.sensor.SlurryPropertyCalculator import SlurryPropertyCalculator
from simulation.battery_model.Slurry import Slurry
import numpy as np
import json
import os
import random
import threading
class MixingMachine(BaseMachine):
    def __init__(self, id, electrode_type, slurry: Slurry, ratio_materials: dict):
        super().__init__(id)
        self.slurry = slurry
        self.electrode_type = electrode_type
        self.volume = 200
        self.temperature = 25
        self.k = random.uniform(0.01, 0.1)  # Random decay constant for viscosity
        self.alpha = random.uniform(0.1, 0.5)  # Random shear-thinning index
        self.ratios = ratio_materials
        self.lock = threading.Lock()
        self.total_time = 0
        self.start_datetime = datetime.now()
        self.output_dir = os.path.join(os.getcwd(), "mixing_output")
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory created at: {self.output_dir}")
        if self.electrode_type == "Anode":
            self.RHO_values = {"AM": 2.26, "CA": 1.8, "PVDF": 1.17, "H2O": 1.0}
            self.WEIGHTS_values = {"a": 0.85, "b": 2.2, "c": 0.3, "s": -0.4}
            with self.lock:
                self.slurry.add("H2O", self.volume * self.ratios["H2O"])
        else:
            self.RHO_values = {"AM": 2.11, "CA": 1.8, "PVDF": 1.78, "NMP": 1.03}
            self.WEIGHTS_values = {"a": 0.9, "b": 2.5, "c": 0.3, "s": -0.5}
            with self.lock:
                self.slurry.add("NMP", self.volume * self.ratios["NMP"])
        self.calculator = SlurryPropertyCalculator(self.RHO_values, self.WEIGHTS_values)
        
    def _format_result(self, is_final=False):
        with self.lock:
            base = {
                "TimeStamp": (self.start_datetime + timedelta(seconds=self.total_time)).isoformat(),
                "Duration (s)": f"{round(self.total_time, 5)} s",
                "Machine ID": self.id,
                "Process": "Mixing",
                "Electrode Type": self.electrode_type,
                "Temperature (C)": f"{round(self.ref_temperature, 2)} °C"
            }
            composition = {
                "AM (kg)": round(getattr(self.slurry, 'AM'), 3),
                "CA (kg)": round(getattr(self.slurry, 'CA'), 3),
                "PVDF (kg)": round(getattr(self.slurry, 'PVDF'), 3),
                f"{self.slurry.solvent} (kg)": round(getattr(self.slurry, self.slurry.solvent), 3)
            }
            properties = {
                "Density (g/cm3)": round(self.calculator.calculate_density(self.slurry)*(1 - self.alpha * (self.temperature - self.ref_temperature)), 4),
                "Viscosity (mPa*s)": round(self.calculator.calculate_viscosity(self.slurry)* np.exp (-self.k * (self.temperature - self.ref_temperature)), 4),
                "YieldStress (Pa)": round(self.calculator.calculate_yield_stress(self.slurry)* np.exp (-self.k * (self.temperature - self.ref_temperature)), 4)
            }
            if is_final:
                base["Final Composition"] = composition
                base["Final Properties"] = properties
            else:
                base.update(composition)
                base.update(properties)
            return base
 
    def _write_json(self, data, filename):
        try:
            timestamp = data["TimeStamp"].replace(":", "-").replace(".", "-")
            unique_filename = f"mixing_output/{self.id}_{timestamp}_{filename}"
            if os.path.exists(unique_filename):
                return
            with self.lock:
                with open(unique_filename, "w") as f:
                    json.dump(data, f, indent=4)
                print(f"Results saved to {unique_filename}")
        except Exception as e:
            print(f"Error writing result to file: {e}")
 
    def _print_result(self, result):
        print(" | ".join(f"{k}: {v}" for k, v in result.items()))
 
    def _mix_component(self, component, step_percent, pause_sec, duration_sec, results_list):
        total_volume = self.volume * self.ratios[component]
        step_volume = step_percent * total_volume
        added_volume = 0.0
        comp_start_time = self.total_time
        last_saved_time = time.time()
        last_saved_result = None
        while self.total_time - comp_start_time < duration_sec:
            self.ref_temperature = np.random.normal(loc=25, scale=1)
            with self.lock:
                self.total_time += pause_sec
                if added_volume < total_volume:
                    add_amt = min(step_volume, total_volume - added_volume)
                    self.slurry.add(component, add_amt)
                    added_volume += add_amt
            result = self._format_result()
            results_list.append(result)
            now = time.time()
            if now - last_saved_time >= 0.1 and result != last_saved_result:
                self._print_result(result)
                filename = f"result_at_{round(self.total_time)}s.json"
                self._write_json(result, filename)
                last_saved_time = now
                last_saved_result = result
            time.sleep(pause_sec)

    def get_final_slurry(self):
        with self.lock:
            return self.slurry

    def _save_final_results(self):
        final_result = self._format_result(is_final=True)
        props = final_result.get("Final Properties", {})
        self.slurry.update_properties(props.get("Viscosity", 0.0), props.get("Density", 0.0), props.get("YieldStress", 0.0))
        print(f"Final properties - Viscosity: {props.get('Viscosity', 0.0):.2f}, Density: {props.get('Density', 0.0):.2f}, Yield Stress: {props.get('YieldStress', 0.0):.2f}")
 
    def run(self, step_percent=0.02, pause_sec=0.1):
        if self.is_on:
            all_results = []
            self._mix_component("PVDF", step_percent, pause_sec, 8, all_results)
            self._mix_component("CA", step_percent, pause_sec, 8, all_results)
            self._mix_component("AM", step_percent, pause_sec, 10, all_results)
            self._save_final_results()
            # Write all results to a summary JSON file
            summary_filename = os.path.join(self.output_dir, f"{self.id}_mixing_summary.json")
            with open(summary_filename, "w") as f:
                json.dump(all_results, f, indent=4)
            print(f"Summary of all mixing data saved to {summary_filename}")
 


