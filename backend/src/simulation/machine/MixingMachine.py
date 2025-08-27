import time
from datetime import datetime, timedelta
from simulation.machine.BaseMachine import BaseMachine
from simulation.sensor.SlurryPropertyCalculator import SlurryPropertyCalculator
from simulation.battery_model.Slurry import Slurry
import json
import os
import random
import threading


class MixingMachine(BaseMachine):
    """
    A machine class for simulating the mixing of battery slurry components.
 
    This class handles the stepwise addition of components to a slurry, simulates
    process parameters (temperature, pressure, RPM), and generates real-time
    simulation data in JSON format. Utility methods are used for formatting results,
    writing output files, and printing process information.
 
    Attributes:
        slurry (Slurry): The slurry being mixed.
        electrode_type (str): Type of electrode being produced ("Anode" or "Cathode").
        RHO_values (dict): Density values for different components.
        WEIGHTS_values (dict): Weight coefficients for property calculations.
        volume (float): Total volume of the slurry in litres.
        ratios (dict): Mixing ratios for different components.
        total_time (float): Total mixing time in seconds.
        calculator (SlurryPropertyCalculator): Calculator for slurry properties.
    """
   
    def __init__(self, id, electrode_type, slurry: Slurry, ratio_materials: dict, connection_string=None):
        """
        Initialise a new MixingMachine instance.
 
        Args:
            id (str): Unique identifier for the machine.
            electrode_type (str): Type of electrode ("Anode" or "Cathode").
            slurry (Slurry): The slurry object to be mixed.
            ratio_materials (dict): Dictionary containing mixing ratios for components.
        """
        super().__init__(id, connection_string)

        self.slurry = slurry
        self.electrode_type = electrode_type
        self.volume = 200
        self.temperature = 25
        self.k_vis = random.uniform(0.01, 0.1)  # Random decay constant for viscosity
        self.k_yield = random.uniform(0.01, 0.1)  # Random decay constant for yield stress
        self.ratios = ratio_materials
        self.lock = threading.Lock()
        self.total_time = 0
        self.start_datetime = datetime.now()
        self.output_dir = os.path.join(os.getcwd(), "mixing_output")
        os.makedirs(self.output_dir, exist_ok=True)


        # Set density values, weight coefficients and initial solvent volume based on electrode type
        if self.electrode_type == "Anode":
            self.RHO_values = {"AM": 2.26, "CA": 1.8, "PVDF": 1.17, "H2O": 1.0}
            self.WEIGHTS_values = {"a": 0.85, "b": 2.2, "c": 0.3, "s": -0.4}
            with self.lock:
                self.slurry.add("H2O", self.volume * self.ratios["H2O"])
        elif self.electrode_type == "Cathode":
            self.RHO_values = {"AM": 2.11, "CA": 1.8, "PVDF": 1.78, "NMP": 1.03} ##TODO To be reviewed
            self.WEIGHTS_values = {"a": 0.9, "b": 2.5, "c": 0.3, "s": -0.5} ##To be changed
            with self.lock:
                self.slurry.add("NMP", self.volume * self.ratios["NMP"])
 
        self.calculator = SlurryPropertyCalculator(self.RHO_values, self.WEIGHTS_values)

    def _format_result(self, is_final=False):
        """
        Format the current or final process data as a dictionary.
        updated with thread safety
        Args:
            is_final (bool): If True, formats the final result with nested composition and properties.
 
        Returns:
            dict: The formatted result data.
        """
        with self.lock:
            base = {
                "TimeStamp": (self.start_datetime + timedelta(seconds=self.total_time)).isoformat(),
                "Duration (s)": round(self.total_time, 5),
                "Machine ID": self.id,
                "Process": "Mixing",
                "Electrode Type": self.electrode_type,
                "Temperature (C)": round(self.ref_temperature, 2)
            }
            composition = {
                "AM (kg)": round(getattr(self.slurry, 'AM'), 3),
                "CA (kg)": round(getattr(self.slurry, 'CA'), 3),
                "PVDF (kg)": round(getattr(self.slurry, 'PVDF'), 3),
                f"{self.slurry.solvent} (kg)": round(getattr(self.slurry, self.slurry.solvent), 3)
            }
            properties = {
                "Density (g/cm3)": round(self.calculator.calculate_density(self.slurry), 4),
                "Viscosity (mPas)": round(self.calculator.calculate_viscosity(self.slurry)* np.exp (-self.k_vis * (self.temperature - self.ref_temperature)), 4),
                "YieldStress (Pa)": round(self.calculator.calculate_yield_stress(self.slurry)* np.exp (-self.k_yield * (self.temperature - self.ref_temperature)), 4)
            }
            if is_final:
                base["Final Composition"] = composition
                base["Final Properties"] = properties
            else:
                base.update(composition)
                base.update(properties)
        return base
 
    def _write_json(self, data, filename):
        """
        Write a dictionary to a JSON file.
 
        Args:
            data (dict): The data to write.
            filename (str): The output filename.
        """
        try:
            # Use the timestamp from the data instead of current time
            timestamp = data["TimeStamp"].replace(":", "-").replace(".", "-")
            unique_filename = f"mixing_output/{self.id}_{timestamp}_{filename}"
            
            # Check if file already exists to prevent duplicates
            if os.path.exists(unique_filename):
                return
                
            with self.lock:  # Use the machine's lock for thread safety
                with open(unique_filename, "w") as f:
                    json.dump(data, f, indent=4)
                print(f"Results saved to {unique_filename}")
                return data
        except Exception as e:
            print(f"Error writing result to file: {e}")
 
    def _print_result(self, result):
        """
        Print the process result in a human-readable format.
 
        Args:
            result (dict): The result data to print.
        """
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
            if now - last_saved_time >= 0.1 and result != last_saved_result:  # Check if data has changed
                filename = f"resultat{round(self.total_time)}s.json"
                data = self._write_json(result, filename)
                if data:
                    self.send_json_to_iothub(data)  # Send to IoT Hub
                    self._print_result(data)  # Print to console
                last_saved_time = now
                last_saved_result = result
            time.sleep(pause_sec)

    def get_final_slurry(self):
        """
        Get the final slurry after mixing is complete.
        
        Returns:
            Slurry: The final mixed slurry object
        """
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

            all_results = []
            self._mix_component("PVDF", step_percent, pause_sec, 8, all_results)
            self._mix_component("CA", step_percent, pause_sec, 8, all_results)
            self._mix_component("AM", step_percent, pause_sec, 10, all_results)

            self._save_final_results() 


            summary_filename = os.path.join(self.output_dir, f"{self.id}_mixing_summary.json")
            with open(summary_filename, "w") as f:
                json.dump(all_results, f, indent=4)
            print(f"Summary of all mixing data saved to {summary_filename}")
