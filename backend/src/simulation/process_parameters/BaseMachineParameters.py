from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class BaseMachineParameters(ABC):
    @abstractmethod
    def validate_parameters(self):
        pass
    
    @abstractmethod
    def get_parameters_dict(self):
        pass
