
from simulation.process_parameters import BaseMachineParameters



class CoatingParameters(BaseMachineParameters):
    coating_speed: float
    gap_height: float
    flow_rate: float
    coating_width: float