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
        self.volume = 200  # Default volume in litres
        self.ratios = ratio_materials
        self.lock = threading.Lock()  # Thread safety lock
        self.total_time = 0
        self.start_datetime = datetime.now()

        # Create mixing_output directory in the current working directory
        self.output_dir = os.path.join(os.getcwd(), "mixing_output")
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory created at: {self.output_dir}")
 
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
                "Duration": round(self.total_time, 5),
                "Machine ID": self.id,
                "Process": "Mixing",
                "Electrode Type": self.electrode_type,
            }
            composition = {
                "AM": round(self.slurry.AM, 3),
                "CA": round(self.slurry.CA, 3),
                "PVDF": round(self.slurry.PVDF, 3),
                f"{self.slurry.solvent}": round(getattr(self.slurry, self.slurry.solvent), 3)
            }
            properties = {
                "Density": round(self.calculator.calculate_density(self.slurry), 4),
                "Viscosity": round(self.calculator.calculate_viscosity(self.slurry), 2),
                "YieldStress": round(self.calculator.calculate_yield_stress(self.slurry), 2)
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
 
    def _mix_component(self, component, step_percent, pause_sec):
        """
        Gradually mix a single component into the slurry, simulating real-time process data.
 
        Args:
            component (str): Component to be mixed.
            step_percent (float): Percentage of total volume to add in each step.
            pause_sec (float): Time to pause between additions in seconds.
        """
        total_volume_to_add = self.volume * self.ratios[component]
        step_volume = step_percent * total_volume_to_add
        steps = int(1 / step_percent)
 
        last_saved_time = time.time()
        last_saved_result = None  # Track last saved result to prevent duplicates

        for _ in range(steps):
            with self.lock:  # Use lock for thread safety
                self.total_time += pause_sec
                self.slurry.add(component, step_volume)

            # Simulate machine parameters
            temperature = round(random.uniform(20, 25), 2)
            pressure = round(random.uniform(1, 2), 2)
            rpm = random.randint(300, 600)

            # Record process data
            result = self._format_result()
            
            # Save results periodically, but only if data has changed
            now = time.time()
            if now - last_saved_time >= 0.1 and result != last_saved_result:  # Check if data has changed
                filename = f"result_at_{round(self.total_time)}s.json"
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
        """
        Save the final mixing results to a JSON file and update the slurry properties
        """
        final_result = self._format_result(is_final=True)
        # Get properties from the final result's nested Final Properties
        final_properties = final_result.get("Final Properties", {})
        viscosity = final_properties.get("Viscosity", 0.0)
        density = final_properties.get("Density", 0.0)
        yield_stress = final_properties.get("YieldStress", 0.0)
        
        # Update slurry properties
        self.slurry.update_properties(viscosity, density, yield_stress)
        
        print(f"Final properties - Viscosity: {viscosity:.2f}, Density: {density:.2f}, Yield Stress: {yield_stress:.2f}")
 
    def run(self, step_percent=0.02, pause_sec=0.1):
        """
        Run the mixing process for all components in the specified order.
 
        Args:
            step_percent (float): Percentage of total volume to add in each step.
            pause_sec (float): Time to pause between additions in seconds.
        """
        if self.is_on:
            from server.main import thread_broadcast
            thread_broadcast(f"Machine {self.id} is already running.") # Broadcast message
            for comp in ["PVDF", "CA", "AM"]:
                self._mix_component(comp, step_percent, pause_sec)

            thread_broadcast(f"Machine {self.id} mixing in progress.") # Broadcast message

            self._save_final_results() 

            thread_broadcast(f"Machine {self.id} mixing completed.") # Broadcast message
 

