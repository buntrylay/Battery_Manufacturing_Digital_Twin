from abc import ABC, abstractmethod

class BaseBatteryState(ABC):
    def __init__(self, timestamp: int):
        self.timestamp = timestamp
    
    @abstractmethod
    def as_dict(self) -> dict:
        """Convert state to dictionary."""
        pass

    @abstractmethod
    def update_properties(self, **kwargs) -> None:
        """Update state properties."""
        pass