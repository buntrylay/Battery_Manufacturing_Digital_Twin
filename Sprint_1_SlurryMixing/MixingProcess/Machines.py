from abc import ABC, abstractmethod
from Slurry import Slurry
from SlurryPropertyCalculator import SlurryPropertyCalculator
from datetime import datetime
import time
import os
import json

class Machine(ABC):
    def __init__(self):
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
    def __init__(self, slurry: Slurry):
        super().__init__()
        self.slurry = slurry
        self.calculator = SlurryPropertyCalculator(slurry)
        self.volume = slurry.total_volume
        self.ratios = {"PVDF": 0.05, "CB": 0.045, "AM": 0.495, "NMP": 0.41}
        self.slurry.add("NMP", self.volume * self.ratios["NMP"])
        self.total_time = 0
    
    def _mix_component(self, component, step_percent, pause_sec):
        target_volume = self.volume * self.ratios[component]
        step_volume = step_percent * target_volume
        steps = int(1 / step_percent)
        os.makedirs("simulation_output", exist_ok=True)

        last_saved_time = time.time()

        for _ in range(steps):
            self.total_time += pause_sec
            self.slurry.add(component, step_volume)
            result = {
                "Time": datetime.now().isoformat(),
                "Component": component,
                "Density": round(self.calculator.calculate_density(), 4),
                "Viscosity": round(self.calculator.calculate_viscosity(), 2),
                "YieldStress": round(self.calculator.calculate_yield_stress(), 2)
            }
            
            now = time.time()
            if now - last_saved_time >= 10:
                print(f"{result['Time']} | {result['Component']} | "
                  f"Density: {result['Density']} | "
                  f"Viscosity: {result['Viscosity']} | "
                  f"Yield Stress: {result['YieldStress']}")
                
                filename = f"simulation_output/result_at_{round(self.total_time)}s.json"
                try:
                    with open(filename, "w") as f:
                        json.dump(result, f, indent=4)
                except Exception as e:
                    print(f"Error writing result to file: {e}")

            time.sleep(pause_sec)
    
    def run(self, step_percent=0.02, pause_sec=1):
        self.turn_on()
        for comp in ["PVDF", "CB", "AM"]:
            self._mix_component(comp, step_percent, pause_sec)