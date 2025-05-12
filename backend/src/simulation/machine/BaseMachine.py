from abc import ABC, abstractmethod

class BaseMachine(ABC):
    """
    Abstract base class representing a generic machine in the battery manufacturing process.
    
    Attributes:
        id (str): Unique identifier for the machine
        is_on (bool): Current operational status of the machine
        calculator (SlurryPropertyCalculator): Calculator for slurry properties
    """
    
    def __init__(self, id):
        """
        Initialise a new Machine instance.
        
        Args:
            id (str): Unique identifier for the machine
        """
        self.id = id
        self.is_on = False
        self.calculator = None

    def turn_on(self):
        """Turn on the machine."""
        self.is_on = True

    def turn_off(self):
        """Turn off the machine."""
        self.is_on = False

    @abstractmethod
    def run(self):
        """Abstract method that must be implemented by concrete machine classes."""
        pass

