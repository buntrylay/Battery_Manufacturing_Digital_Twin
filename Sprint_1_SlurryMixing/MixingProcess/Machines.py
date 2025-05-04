from abc import ABC, abstractmethod
from Slurry import Slurry
from SlurryPropertyCalculator import SlurryPropertyCalculator
from datetime import datetime
import time

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
        self.results = []
    
    def _mix_component(self, component, step_percent, pause_sec):
        target_volume = self.volume * self.ratios[component]
        step_volume = step_percent * target_volume
        steps = int(1 / step_percent)
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
            self.results.append(result)
            time.sleep(pause_sec)
    
    def run(self, step_percent=0.02, pause_sec=1):
        self.turn_on()
        for comp in ["PVDF", "CB", "AM"]:
            self._mix_component(comp, step_percent, pause_sec)