from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime
import time
from backend.src.simulation.event_bus.events import EventBus, MachineEventType
from simulation.process_parameters import BaseMachineParameters
from simulation.battery_model.BaseModel import BaseModel
from simulation.helper.LocalDataSaver import LocalDataSaver
from simulation.helper.IoTHubSender import IoTHubSender
from server.notification_queue import notify_machine_status


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
        connection_string=None,
        data_broadcast_fn=None,
        data_broadcast_interval_sec=5,
    ):
        self.process_name = process_name
        self.battery_model = battery_model
        self.machine_parameters = machine_parameters
        self.state = False
        self.current_process_start_time = None
        self.current_time_step = 0
        # Event bus related
        self.event_bus = event_bus
        # WebSocket related
        self.data_broadcast_fn = data_broadcast_fn
        self.data_broadcast_interval_sec = data_broadcast_interval_sec
        self._last_broadcast_monotonic = None
        # temporary fix
        self.batch_id = None

    @abstractmethod
    def receive_model_from_previous_process(self, previous_model: BaseModel):
        pass

    @abstractmethod
    def input_model(self, model: BaseModel):
        pass

    @abstractmethod
    def empty_model(self) -> BaseModel:
        returned_model = self.battery_model
        self.battery_model = None
        return returned_model

    def update_machine_parameters(self, machine_parameters: BaseMachineParameters):
        """Update the machine parameters."""
        self.machine_parameters = machine_parameters

    def _maybe_broadcast_data(self, payload):
        """
        If data broadcasting is configured, send JSON payload no more frequently than
        data_broadcast_interval_sec. Uses a monotonic clock to avoid wall-clock drift.
        """
        try:
            notify_machine_status(
                machine_id=self.process_name,
                line_type=self.process_name.split("_")[-1],
                process_name=self.process_name,
                status="data_generated",
                data=payload,
            )
            print("Generated data pushed to notification queue!")
        except Exception as e:
            # Never let broadcasting break simulation loop
            print(f"Failed to broadcast data via callback function: {e}")

    def turn_on(self):
        """Turn on the machine."""
        self.state = True
        self.start_datetime = datetime.now()
        self.current_process_start_time = datetime.now()
        self.__emit_event(
            MachineEventType.TURNED_ON,
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
            MachineEventType.TURNED_OFF,
            data={
                "message": f"{self.process_name} was turned off at {datetime.now().isoformat()}"
            },
        )

    def pre_run_check(self):
        """Pre-run check for the machine."""
        if self.battery_model is None:
            raise ValueError("Battery model is not set")
        if self.machine_parameters is None:
            raise ValueError("Machine parameters are not set")
        if self.total_steps is None:
            self.calculate_total_steps()
        return True

    def calculate_total_steps(self):
        """Calculate the total number of steps for the machine."""
        pass

    def get_current_state(self, process_specifics=None):
        """Get the current properties of the machine."""
        if self.state:
            return {
                "timestamp": datetime.now().isoformat(),
                "state": "On",
                "duration": round(self.current_time_step, 2),
                "process": self.process_name,
                "battery_model": self.battery_model.get_properties(),
                "machine_parameters": asdict(self.machine_parameters),
                "process_specifics": process_specifics,
            }
        else:
            return {
                "timestamp": datetime.now().isoformat(),
                "process": self.process_name,
                "state": "Off",
                "machine_parameters": asdict(self.machine_parameters),
                "process_specifics": process_specifics,
            }

    def append_process_specifics(self, process_specifics):
        """Append the process state to the current properties."""
        return {
            "process_specifics": process_specifics,
        }

    @abstractmethod
    def run(self):
        """Abstract method that must be implemented by concrete machine classes."""
        pass

    @abstractmethod
    def step_logic(self, t: int):
        """Abstract method that must be implemented by concrete machine classes."""
        pass

    @abstractmethod
    def validate_parameters(self, parameters: dict):
        """Validate the parameters."""
        pass

    # TODO: This is a future feature to run the simulation in a standardised way
    def run_simulation(self, total_steps=100, pause_between_steps=0.1, verbose=True):
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
                print(f"Machine {self.process_name} is running for {total_steps} steps")
            for t in range(0, self.total_steps):
                self.current_time_step = t  # current time step
                self.step_logic(t)
                self.battery_model.update_properties(self.machine_parameters)
                self.__emit_event(
                    MachineEventType.STATUS_UPDATE,
                    data={
                        "message": f"Machine {self.process_name} is running for {t} steps",
                        "machine_state": self.get_current_state(),
                    },
                )
                if verbose:
                    print("Current machine state: ", self.get_current_state())
                time.sleep(pause_between_steps)
            self.turn_off()

    def __emit_event(self, event_type: MachineEventType, data: dict = None):
        """Emit an event to the event bus."""
        if self.event_bus is not None:
            self.event_bus.emit_machine_event(
                machine_id=self.process_name,
                event_type=event_type,
                data=data,
            )
