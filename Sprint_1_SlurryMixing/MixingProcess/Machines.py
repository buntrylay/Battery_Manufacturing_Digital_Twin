from abc import ABC, abstractmethod

class Machine(ABC):
    def __init__(self):
        self.is_on = False
        self.calculator = None