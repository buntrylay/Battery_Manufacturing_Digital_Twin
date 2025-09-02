from abc import ABC, abstractmethod

#simple Nase class for battery models
class BaseModel(ABC):

    @abstractmethod
    def get_properties(self):
        pass

    @abstractmethod
    def update_properties(self):
        pass