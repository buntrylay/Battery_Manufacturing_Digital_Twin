from abc import ABC, abstractmethod
from Slurry import Slurry
from SlurryPropertyCalculator import SlurryPropertyCalculator
from datetime import datetime
import time
import os
import json
import random

class Machine(ABC):
    def __init__(self, id):
        self.id = id
        self.is_on = False
        self.calculator = None

    def turn_on(self):
        self.is_on = True

    def turn_off(self):
        self.is_on = False

    @abstractmethod
    def run(self):
        pass

class MixingMachine(Machine):
    def __init__(self, id, electrode_type, slurry: Slurry, ratio_materials: dict):
        super().__init__(id)
        self.slurry = slurry
        self.electrode_type = electrode_type

        if self.electrode_type == "Anode":
            self.RHO_values = {"AM": 2.26, "CA": 1.8, "PVDF": 1.78, "H2O": 1.0}
            self.WEIGHTS_values = {"a": 0.9, "b": 2.5, "c": 0.3, "s": -0.5}
            self.slurry.add("H2O", self.volume * self.ratios["H2O"])
        elif self.electrode_type == "Cathode":
            self.RHO_values = {"AM": 2.26, "CA": 2.26, "PVDF": 1.78, "NMP": 1.0} ##To be changed
            self.WEIGHTS_values = {"a": 0.9, "b": 2.5, "c": 0.3, "s": -0.5} ##To be changed
            self.slurry.add("NMP", self.volume * self.ratios["NMP"])

        self.calculator = SlurryPropertyCalculator(slurry, self.RHO_values, self.WEIGHTS_values)
        self.volume = 200
        self.ratios = ratio_materials
        self.total_time = 0
    
    def _mix_component(self, component, step_percent, pause_sec):
        total_volume_to_add = self.volume * self.ratios[component]
        step_volume = step_percent * total_volume_to_add
        steps = int(1 / step_percent)
        os.makedirs("simulation_output", exist_ok=True)

        last_saved_time = time.time()

        for _ in range(steps):
            self.total_time += pause_sec
            self.slurry.add(component, step_volume)

            result = {
                "Time": datetime.now().isoformat(),
                "Machine ID": self.id,
                "Process": "Mixing",
                "Component": component,
                "Density": round(self.calculator.calculate_density(), 4),
                "Viscosity": round(self.calculator.calculate_viscosity(), 2),
                "YieldStress": round(self.calculator.calculate_yield_stress(), 2)
            }
            
            now = time.time()
            if now - last_saved_time >= 5:
                print(f"{result['Time']} | "
                    f"{result['Machine ID']} | "
                    f"{result['Process']} | "
                    f"{result['Component']} | "
                    f"Density: {result['Density']} | "
                    f"Viscosity: {result['Viscosity']} | "
                    f"Yield Stress: {result['YieldStress']}")
                
                filename = f"simulation_output/result_at_{round(self.total_time)}s.json"
                try:
                    with open(filename, "w") as f:
                        json.dump(result, f, indent=4)
                except Exception as e:
                    print(f"Error writing result to file: {e}")
                
                last_saved_time = now  # Update the last saved time

            time.sleep(pause_sec)
    
    def run(self, step_percent=0.02, pause_sec=1):
        if self.is_on:
            for comp in ["PVDF", "CA", "AM"]:
                self._mix_component(comp, step_percent, pause_sec)
