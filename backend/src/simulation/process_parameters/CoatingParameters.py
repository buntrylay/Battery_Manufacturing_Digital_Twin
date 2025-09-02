
from simulation.process_parameters import BaseMachineParameters



class CoatingParameters(BaseMachineParameters):
    coating_speed: float
    gap_height: float
    flow_rate: float
    coating_width: float

    def validate_parameters(self):
        if self.coating_speed <= 0:
            raise ValueError("Coating speed must be greater than 0")
        if self.gap_height <= 0:
            raise ValueError("Gap height must be greater than 0")
        if self.flow_rate <= 0:
            raise ValueError("Flow rate must be greater than 0")
        if self.coating_width <= 0:
            raise ValueError("Coating width must be greater than 0")
        return 
    
    def get_parameters_dict(self):
        return {
            "coating_speed": self.coating_speed,
            "gap_height": self.gap_height,
            "flow_rate": self.flow_rate,
            "coating_width": self.coating_width
        }