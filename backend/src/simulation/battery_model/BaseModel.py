from abc import ABC, abstractmethod


class BaseModel(ABC):

    # def __init__(self, previous_model: "BaseModel" = None):
    #     self.previous_model = previous_model

    @abstractmethod
    def get_properties(self):
        pass

    @abstractmethod
    def update_properties(self):
        pass