
from dataclasses import dataclass
from simulation.process_parameters import BaseMachineParameters
@dataclass
class DryingParameters(BaseMachineParameters):
    web_speed: float
    wet_thickness: float
    solid_content: float

    def validate_parameters(self):
        if self.wet_thickness <= 0:
            raise ValueError("Wet thickness must be positive.")
        if not (0 < self.solid_content < 1):
            raise ValueError("Solid content must be between 0 and 1.")
        if self.web_speed <= 0:
            raise ValueError("Web speed must be positive.")
