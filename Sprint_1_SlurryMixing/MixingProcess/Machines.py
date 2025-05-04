from abc import ABC, abstractmethod
from Slurry import Slurry
from SlurryPropertyCalculator import SlurryPropertyCalculator

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