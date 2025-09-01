from abc import ABC, abstractmethod


class BaseModel(ABC):

    @abstractmethod
    def get_properties(self):
        pass

    @abstractmethod
    def update_properties(self):
        pass