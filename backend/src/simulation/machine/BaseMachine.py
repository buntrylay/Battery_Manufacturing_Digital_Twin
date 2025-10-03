from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime
import time
from simulation.process_parameters import BaseMachineParameters
from simulation.battery_model.BaseModel import BaseModel
from simulation.helper.LocalDataSaver import LocalDataSaver
from simulation.helper.IoTHubSender import IoTHubSender
from server.notification_queue import notify_machine_status


class BaseMachine(ABC):
    """
    Abstract base class representing a generic machine in the battery manufacturing process.

    Attributes:
        id (str): Unique identifier for the machine
        is_on (bool): Current operational status of the machine
        calculator (SlurryPropertyCalculator): Calculator for slurry properties
    """

    def __init__(
        self,
        process_name,
        battery_model: BaseModel = None,
        machine_parameters: BaseMachineParameters = None,
        connection_string=None,
        data_broadcast_fn=None,
        data_broadcast_interval_sec=5,
        **kwargs,
    ):
        """
        Initialise a new Machine instance.

        Args:
            process_name (str): The name of the process
            battery_model (BaseModel): The battery model to be used
            machine_parameters (dataclass): The machine parameters to be used
            connection_string (str): The connection string for the IoT Hub
            **kwargs: Additional keyword arguments (probably for properties that are not in the machine parameters and specific to the machine)
        """
        self.process_name = process_name
        self.battery_model = battery_model
        self.machine_parameters = machine_parameters
        self.state = False
        self.current_process_start_time = None
        self.current_time_step = 0

        self.data_broadcast_fn = data_broadcast_fn
        self.data_broadcast_interval_sec = data_broadcast_interval_sec
        self._last_broadcast_monotonic = None
        # temporary fix
        self.batch_id = None

    @abstractmethod
    def receive_model_from_previous_process(self, previous_model: BaseModel):
        pass

    def empty_battery_model(self):
        """Empty the model."""
        self.battery_model = None

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
        # Emit event instead of direct notification
        # if event_bus is not None:
        #     event_bus.emit_machine_event(
        #         machine_id=self.process_name,
        #         process_name=self.process_name,
        #         event_type=MachineEventType.TURNED_ON,
        #         data={
        #             "stage": "turned_on",
        #             "message": f"{self.process_name} turned on",
        #         },
        #     )
        self.current_process_start_time = datetime.now()
        notify_machine_status(
            machine_id=self.process_name,
            line_type=self.process_name.split("_")[
                -1
            ],  # Get the last part after splitting
            process_name=self.process_name,
            status="running",
            data={"message": f"{self.process_name} was turned on"},
        )

    def turn_off(self):
        """Turn off the machine."""
        self.state = False
        self.total_time = 0
        # Emit event instead of direct notification
        # if event_bus is not None:
        #     event_bus.emit_machine_event(
        #         machine_id=self.process_name,
        #         line_type=(
        #             self.process_name.split("_")[1]
        #             if "_" in self.process_name
        #             else "unknown"
        #         ),
        #         process_name=self.process_name,
        #         event_type=MachineEventType.TURNED_OFF,
        #         data={
        #             "stage": "turned_off",
        #             "message": f"{self.process_name} turned off",
        #         },
        #     )
        self.current_time_step = 0
        notify_machine_status(
            machine_id=self.process_name,
            line_type=self.process_name.split("_")[
                -1
            ],  # Get the last part after splitting
            process_name=self.process_name,
            status="idle",
            data={"message": f"{self.process_name} was turned off"},
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

    def clean_up(self):
        """Clean up the machine."""
        self.turn_off()
        self.battery_model = None
        self.state = False
        self.current_time_step = 0
        self.current_process_start_time = None

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
                # notify the machine status
                # Send progress updates every 10 steps
                if verbose:
                    print(self.get_current_state())
                time.sleep(pause_between_steps)
            self.turn_off()
