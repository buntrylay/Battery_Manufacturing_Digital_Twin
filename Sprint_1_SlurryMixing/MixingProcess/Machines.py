from abc import ABC, abstractmethod
from Slurry import Slurry
from SlurryPropertyCalculator import SlurryPropertyCalculator
from datetime import datetime
import time
import os
import json
import random

class Machine(ABC):
    """
    Abstract base class representing a generic machine in the battery manufacturing process.
    
    Attributes:
        id (str): Unique identifier for the machine
        is_on (bool): Current operational status of the machine
        calculator (SlurryPropertyCalculator): Calculator for slurry properties
    """
    
    def __init__(self, id):
        """
        Initialise a new Machine instance.
        
        Args:
            id (str): Unique identifier for the machine
        """
        self.id = id
        self.is_on = False
        self.calculator = None

    def turn_on(self):
        """Turn on the machine."""
        self.is_on = True

    def turn_off(self):
        """Turn off the machine."""
        self.is_on = False

    @abstractmethod
    def run(self):
        """Abstract method that must be implemented by concrete machine classes."""
        pass

class MixingMachine(Machine):
    """
    A concrete machine class for mixing battery slurry components.
    
    Attributes:
        slurry (Slurry): The slurry being mixed
        electrode_type (str): Type of electrode being produced ("Anode" or "Cathode")
        RHO_values (dict): Density values for different components
        WEIGHTS_values (dict): Weight coefficients for property calculations
        volume (float): Total volume of the slurry
        ratios (dict): Mixing ratios for different components
        total_time (float): Total mixing time in seconds
    """
    
    def __init__(self, id, electrode_type, slurry: Slurry, ratio_materials: dict):
        """
        Initialise a new MixingMachine instance.
        
        Args:
            id (str): Unique identifier for the machine
            electrode_type (str): Type of electrode ("Anode" or "Cathode")
            slurry (Slurry): The slurry object to be mixed
            ratio_materials (dict): Dictionary containing mixing ratios for components
        """
        super().__init__(id)
        self.slurry = slurry
        self.electrode_type = electrode_type
        self.volume = 200  # Default volume in litres
        self.ratios = ratio_materials

        # Set density values, weight coefficients and initial solvent volume based on electrode type
        if self.electrode_type == "Anode":
            self.RHO_values = {"AM": 2.26, "CA": 1.8, "PVDF": 1.78, "H2O": 1.0}
            self.WEIGHTS_values = {"a": 0.9, "b": 2.5, "c": 0.3, "s": -0.5}
            self.slurry.add("H2O", self.volume * self.ratios["H2O"])
        elif self.electrode_type == "Cathode":
            self.RHO_values = {"AM": 2.26, "CA": 2.26, "PVDF": 1.78, "NMP": 1.0} ##To be changed
            self.WEIGHTS_values = {"a": 0.9, "b": 2.5, "c": 0.3, "s": -0.5} ##To be changed
            self.slurry.add("NMP", self.volume * self.ratios["NMP"])

        self.calculator = SlurryPropertyCalculator(self.RHO_values, self.WEIGHTS_values)
        self.total_time = 0
    
    def _mix_component(self, component, step_percent, pause_sec):
        """
        Mix a single component into the slurry gradually.
        
        Args:
            component (str): Component to be mixed
            step_percent (float): Percentage of total volume to add in each step
            pause_sec (float): Time to pause between additions in seconds
        """
        total_volume_to_add = self.volume * self.ratios[component]
        step_volume = step_percent * total_volume_to_add
        steps = int(1 / step_percent)
        os.makedirs("simulation_output", exist_ok=True)

        last_saved_time = time.time()

        for _ in range(steps):
            self.total_time += pause_sec
            self.slurry.add(component, step_volume)

            # Simulate machine parameters
            temperature = round(random.uniform(20, 25), 2)
            pressure = round(random.uniform(1, 2), 2)
            rpm = random.randint(300, 600)

            # Record process data
            result = {
                "TimeStamp": datetime.now().isoformat(),
                "Duration": round(self.total_time, 5),
                "Machine ID": self.id,
                "Process": "Mixing",
                "AM": round(self.slurry.AM, 3),
                "CB": round(self.slurry.CA, 3),
                "PVDF": round(self.slurry.PVDF, 3),
                f"{self.slurry.solvent}": round(self.slurry.H2O, 3) if self.electrode_type == "Anode" else round(self.slurry.NMP, 3),
                "Temperature": temperature,
                "Pressure": pressure,
                "Speed (RPM)": rpm,
                "Density": round(self.calculator.calculate_density(self.slurry), 4),
                "Viscosity": round(self.calculator.calculate_viscosity(self.slurry), 2),
                "YieldStress": round(self.calculator.calculate_yield_stress(self.slurry), 2)
            }
            
            # Save results every 5 seconds
            now = time.time()
            if now - last_saved_time >= 5:
                print(f"{result['TimeStamp']} | "
                      f"{result['Duration']} | "
                    f"{result['Machine ID']} | "
                    f"{result['Process']} | "
                    f"{result['AM']} | "
                    f"{result['CB']} | "
                    f"{result['PVDF']} | "
                    f"{result[f'{self.slurry.solvent}']} | "
                    f"Temperature: {result['Temperature']} | "
                    f"Pressure: {result['Pressure']} | "
                    f"Speed (RPM): {result['Speed (RPM)']} | "
                    f"Density: {result['Density']} | "
                    f"Viscosity: {result['Viscosity']} | "
                    f"Yield Stress: {result['YieldStress']}")
                
                filename = f"simulation_output/result_at_{round(self.total_time)}s.json"
                try:
                    with open(filename, "w") as f:
                        json.dump(result, f, indent=4)
                except Exception as e:
                    print(f"Error writing result to file: {e}")
                
                last_saved_time = now

            time.sleep(pause_sec)
    
    def _save_final_results(self):
        """Save the final mixing results to a JSON file."""
        final_result = {
            "TimeStamp": datetime.now().isoformat(),
            "Duration": round(self.total_time, 5),
            "Machine ID": self.id,
            "Process": "Mixing",
            "Electrode Type": self.electrode_type,
            "Final Composition": {
                "AM": round(self.slurry.AM, 3),
                "CB": round(self.slurry.CA, 3),
                "PVDF": round(self.slurry.PVDF, 3),
                f"{self.slurry.solvent}": round(self.slurry.H2O, 3) if self.electrode_type == "Anode" else round(self.slurry.NMP, 3)
            },
            "Final Properties": {
                "Density": round(self.calculator.calculate_density(self.slurry), 4),
                "Viscosity": round(self.calculator.calculate_viscosity(self.slurry), 2),
                "YieldStress": round(self.calculator.calculate_yield_stress(self.slurry), 2)
            }
        }
        
        filename = f"simulation_output/final_results_{self.id}.json"
        try:
            with open(filename, "w") as f:
                json.dump(final_result, f, indent=4)
            print(f"\nFinal results saved to {filename}")
        except Exception as e:
            print(f"Error saving final results: {e}")

    def run(self, step_percent=0.02, pause_sec=1):
        """
        Run the mixing process for all components.
        
        Args:
            step_percent (float): Percentage of total volume to add in each step
            pause_sec (float): Time to pause between additions in seconds
        """
        if self.is_on:
            for comp in ["PVDF", "CA", "AM"]:
                self._mix_component(comp, step_percent, pause_sec)
            self._save_final_results()
