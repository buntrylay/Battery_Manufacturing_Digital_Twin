from abc import ABC, abstractmethod
from simulation.process_parameters import BaseMachineParameters

#simple Nase class for battery models
class BaseModel(ABC):

    # def __init__(self, previous_model: "BaseModel" = None):
    #     self.previous_model = previous_model

    @abstractmethod
    def get_properties(self):
        pass

    @abstractmethod
    def update_properties(self, machine_parameters: BaseMachineParameters):
        pass