from abc import ABC, abstractmethod

class Machine(ABC):
    def __init__(self):
        self.is_on = False
        self.calculator = None

    def turn_on(self):
        self.is_on = True

    def turn_off(self):
        self.is_on = False