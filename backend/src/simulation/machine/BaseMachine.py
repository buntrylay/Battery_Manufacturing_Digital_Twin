from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime
import time
from simulation.event_bus.events import EventBus, PlantSimulationEventType
from simulation.process_parameters import BaseMachineParameters
from simulation.battery_model.BaseModel import BaseModel


class BaseMachine(ABC):
    """
    Abstract base class representing a generic machine in the battery manufacturing process.
    """

    def __init__(
        self,
        process_name,
        battery_model: BaseModel = None,
        machine_parameters: BaseMachineParameters = None,
        event_bus: EventBus = None,
    ):
        self.process_name = process_name
        self.battery_model = battery_model
        self.machine_parameters = machine_parameters
        self.state = False
        self.current_process_start_time = None
        self.current_time_step = 0
        # Event bus related
        self.event_bus = event_bus
        # simulation-related
        self.total_steps = None  # required
        self.pause_between_steps = 0.1

    @abstractmethod
    def receive_model_from_previous_process(self, previous_model: BaseModel):
        # could be improved
        pass

    def empty_model(self) -> BaseModel:
        returned_model = self.battery_model
        self.battery_model = None
        return returned_model

    def update_machine_parameters(self, machine_parameters: BaseMachineParameters):
        """Update the machine parameters."""
        self.machine_parameters = machine_parameters

    def turn_on(self):
        """Turn on the machine."""
        self.state = True
        self.start_datetime = datetime.now()
        self.current_process_start_time = datetime.now()
        self.__emit_event(
            PlantSimulationEventType.MACHINE_TURNED_ON,
            data={
                "message": f"{self.process_name} was turned on at {self.current_process_start_time.isoformat()}"
            },
        )

    def turn_off(self):
        """Turn off the machine."""
        self.state = False
        self.total_time = 0
        self.current_time_step = 0
        self.current_process_start_time = None
        self.__emit_event(
            PlantSimulationEventType.MACHINE_TURNED_OFF,
            data={
                "message": f"{self.process_name} was turned off at {datetime.now().isoformat()}"
            },
        )

    def pre_run_check(self):
        """Pre-run check for the machine."""
        if self.battery_model is None:
            return False
        if self.machine_parameters is None:
            return False
        if self.total_steps is None:
            self.calculate_total_steps()
        return True

    def calculate_total_steps(self):
        """Calculate the total number of steps for the machine."""
        pass

    def get_current_state(self, process_specifics=None):
        """Get the current properties of the machine."""
        # Safely handle machine_parameters
        machine_params_dict = {}
        if self.machine_parameters is not None:
            try:
                machine_params_dict = asdict(self.machine_parameters)
            except TypeError:
                # Fallback: if not a dataclass, try to get dict representation
                if hasattr(self.machine_parameters, 'get_parameters_dict'):
                    machine_params_dict = self.machine_parameters.get_parameters_dict()
                elif hasattr(self.machine_parameters, '__dict__'):
                    machine_params_dict = self.machine_parameters.__dict__.copy()
                else:
                    machine_params_dict = {"error": "Unable to serialize parameters"}
        
        if self.state:
            battery_model_props = {}
            if self.battery_model is not None:
                try:
                    battery_model_props = self.battery_model.get_properties()
                except Exception:
                    battery_model_props = {"error": "Unable to get battery model properties"}
            
            return {
                "timestamp": datetime.now().isoformat(),
                "state": "On",
                "duration": round(self.current_time_step, 2),
                "process": self.process_name,
                "battery_model": battery_model_props,
                "machine_parameters": machine_params_dict,
                "process_specifics": process_specifics,
            }
        else:
            return {
                "timestamp": datetime.now().isoformat(),
                "process": self.process_name,
                "state": "Off",
                "machine_parameters": machine_params_dict,
                "process_specifics": process_specifics,
            }

    def append_process_specifics(self, process_specifics):
        """Append the process state to the current properties."""
        return {
            "process_specifics": process_specifics,
        }

    @abstractmethod
    def step_logic(self, t: int, verbose: bool):
        """Abstract method that must be implemented by concrete machine classes."""
        pass

    @abstractmethod
    def validate_parameters(self, parameters):
        """Validate the parameters.
        
        Args:
            parameters: Either a dictionary of parameters or a parameter object
        """
        pass

    def run_simulation(self, verbose: bool = True):
        """Run the simulation.
        Args:
            total_steps (int): The total number of steps to run the simulation for
            pause_between_steps (float): The pause between steps in seconds
            verbose (bool): Whether to print to the console when running the simulation
        """
        # make sure the machine has a model to simulate and some parameters!
        if self.pre_run_check():
            # turn on the machine
            self.turn_on()
            if verbose:
                print(
                    f"Machine {self.process_name} is going to be running for {self.total_steps} steps"
                )
            for t in range(0, self.total_steps):
                self.current_time_step = t  # current time step
                try:
                    self.step_logic(t, verbose)
                except RuntimeError as rte:
                    if verbose:
                        print("Plant Warning: Voltage exceeded! ", rte)
                    self.__emit_event(
                        PlantSimulationEventType.MACHINE_SIMULATION_ERROR,
                        {
                            "error": "Plant Warning: Voltage exceeded! in Formation Cycling"
                        },
                    )
                    break
                self.battery_model.update_properties(self.machine_parameters, t)
                self.__emit_event(
                    PlantSimulationEventType.MACHINE_DATA_GENERATED,
                    data={
                        "message": f"Machine {self.process_name} has been running for {t} steps",
                        "machine_state": self.get_current_state(),
                    },
                )
                if verbose:
                    print("Current machine state: ", self.get_current_state())
                time.sleep(self.pause_between_steps)
            self.turn_off()
        else:
            raise Exception("Implementation error!")

    def __emit_event(self, event_type: PlantSimulationEventType, data: dict = None):
        """Emit an event to the event bus."""
        processed_data = None
        if data is not None:
            processed_data = {"machine_id": self.process_name, **data}
        if self.event_bus is not None:
            self.event_bus.emit_plant_simulation_event(
                event_type=event_type,
                data=processed_data,
            )
