from abc import ABC, abstractmethod
from datetime import datetime
import json
import time

class Simulation(ABC):
    '''All simulation time-based aspects are handled here.'''
    def __init__(self, id: str, actual_process_duration: int, speed_factor: float):
        self.id = id
        # actual real-world information
        # maybe no need to have this?
        self.actual_process_duration = actual_process_duration # in minutes

        # simulation time information
        # maybe no need to have this?
        self.simulation_time = actual_process_duration * 60 * speed_factor # in seconds

        self.simulation_time_step = self.calculate_total_steps() # integer
        self.speed_factor = speed_factor # like x10, x100, etc.
        self.pause_time = 1 # in seconds

        # real-time information
        self.start_time = datetime.now()
        self.current_time = self.start_time

    
    def run(self) -> None:
        """Run the simulation stage."""
        for t in range(self.simulation_time):
            self.step_logic(t)
            time.sleep(self.pause_time)
    

    @abstractmethod
    def calculate_total_steps(self) -> int:
        """Calculate the total number of steps for the simulation."""
        raise NotImplementedError("Subclasses must implement this method")
    
    @abstractmethod
    def step_logic(self, t: int) -> None:
        """Execute one step of the simulation logic."""
        raise NotImplementedError("Subclasses must implement this method")

    # will have default implementation
    def save_data(self, data: dict) -> None:
        """Save the data into a local file. Maybe based on the simulation time step? Or can it have flexibility?"""
        # save the data into a local file
        with open(f"data_from_{self.id}_{self.current_time}.json", "w") as f:
            json.dump(data, f)

    def send_data(self, data: dict) -> None:
        """Send the data to any external system. Maybe based on the simulation time step? Or can it have flexibility?"""
        raise NotImplementedError("Subclasses must implement this method")
    