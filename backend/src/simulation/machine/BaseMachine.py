from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime
import time
from simulation.process_parameters import BaseMachineParameters
from simulation.battery_model.BaseModel import BaseModel
from simulation.helper.LocalDataSaver import LocalDataSaver
from simulation.helper.IoTHubSender import IoTHubSender
# from server.notification_queue import notify_machine_status

try:
    from server.notification_queue import notify_machine_status
except ImportError:
    def notify_machine_status(*args, **kwargs):
        return None

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
        # Helpers
        self.local_saver = LocalDataSaver(process_name)
        self.iot_sender = IoTHubSender(connection_string)
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

    # delegate to a different class
    def send_json_to_iothub(self, data):
        """
        Send a JSON-serializable dictionary to Azure IoT Hub via MQTT.

        Args:
            data (dict): The data to send.
        """
        sent = self.iot_sender.send_json(data)
        if sent:
            print(f"Sent data to IoT Hub for machine {self.process_name}")
        else:
            print("IoT Hub client not initialised or send failed.")

    # delegate to a different class
    def save_data_to_local_folder(self):
        """
        Save data to a local folder.
        """
        try:
            current_properties = self.get_current_state()
            print(current_properties)
            path = self.local_saver.save_current_state(
                current_properties, self.current_time_step
            )
            print(f"Data saved to {path}")
        except Exception as e:
            print(f"Failed to save data to local folder: {e}")

    # def _maybe_broadcast_data(self, payload):
    #     """
    #     If data broadcasting is configured, send JSON payload no more frequently than
    #     data_broadcast_interval_sec. Uses a monotonic clock to avoid wall-clock drift.
    #     """
    #     try:
    #         notify_machine_status(
    #             machine_id=self.process_name,
    #             line_type=self.process_name.split('_')[-1],
    #             process_name=self.process_name,
    #             status="data_generated",
    #             data=payload
    #         )
    #         print("Generated data pushed to notification queue!")
    #     except Exception as e:
    #         # Never let broadcasting break simulation loop
    #         print(f"Failed to broadcast data via callback function: {e}")

    # delegate to a different class
    def save_all_results(self, results):
        """
        Save all results to a local folder.
        """
        try:
            path = self.local_saver.save_all_results(results)
            print(f"Summary of all results saved to {path}")
        except Exception as e:
            print(f"Failed to save summary of all results: {e}")

    def turn_on(self):
        """Turn on the machine."""
        self.state = True
        self.current_process_start_time = datetime.now()
        # notify_machine_status(
        #     machine_id=self.process_name,
        #     line_type=self.process_name.split("_")[
        #         -1
        #     ],  # Get the last part after splitting
        #     process_name=self.process_name,
        #     status="running",
        #     data={"message": f"{self.process_name} was turned on"},
        # )

    def turn_off(self):
        """Turn off the machine."""
        self.state = False
        self.current_time_step = 0
        # notify_machine_status(
        #     machine_id=self.process_name,
        #     line_type=self.process_name.split("_")[
        #         -1
        #     ],  # Get the last part after splitting
        #     process_name=self.process_name,
        #     status="idle",
        #     data={"message": f"{self.process_name} was turned off"},
        # )

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
        state = {
            "timestamp": datetime.now().isoformat(),
            "state": "On" if self.state else "Off",
            "duration": round(self.current_time_step, 2),
            "process": self.process_name,
            "temperature_C": (
                round(self.battery_model.temperature, 2)
                if self.state and hasattr(self.battery_model, "temperature")
                else None
            ),
            "battery_model": (
                self.battery_model.get_properties() if self.battery_model else {}
            ),
            "machine_parameters": (
                asdict(self.machine_parameters) if self.machine_parameters else {}
            ),
            "process_specifics": process_specifics,
        }
        # Add context if available
        if hasattr(self, "batch_id"):
            state["batch_id"] = self.batch_id

        return state

    def append_process_specifics(self, process_specifics):
        """Append the process state to the current properties."""
        return {
            "process_specifics": process_specifics,
        }

# this serve as a reference to all machine run_simulation further implementation
    # @abstractmethod
    # def run(self):
    #     """Abstract method that must be implemented by concrete machine classes."""
    #     pass

    @abstractmethod
    def step_logic(self, t: int):
        """Abstract method that must be implemented by concrete machine classes."""
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
                self.current_time_step = t # current time step
                self.step_logic(t)
                try:
                    self.battery_model.update_properties(self.machine_parameters, t)
                except TypeError:
                    self.battery_model.update_properties(self.machine_parameters)
                # notify the machine status
                # Send progress updates every 10 steps
                if verbose:
                    print(self.get_current_state())
                time.sleep(pause_between_steps)
            self.turn_off()

    def clean_up(self):
        """Clean up the machine."""
        self.turn_off()
        self.battery_model = None
        self.state = False
        self.current_time_step = 0
        self.current_process_start_time = None

    # idea to standardise the step logic with decorator @abstractmethod
    @abstractmethod
    def step_logic(self, t: int):
        """
        Abstract method that must be implemented by concrete machine classes.
        This method is called at each step of the simulation.
        """
        pass

    # def add_notification(self):
    #     notify_machine_status()

    @abstractmethod
    def validate_parameters(self, parameters: dict):
        """Validate the parameters."""
        pass
