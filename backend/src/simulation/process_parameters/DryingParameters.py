from dataclasses import dataclass
from simulation.process_parameters import BaseMachineParameters

@dataclass
class DryingParameters(BaseMachineParameters):
    web_speed: float   # user input

    def validate_parameters(self):
        if self.web_speed <= 0:
            raise ValueError("Web speed must be greater than 0")
        return

    def get_parameters_dict(self):
        return {
            "web_speed": self.web_speed,
        }
