from abc import ABC, abstractmethod
from dataclasses import asdict
from datetime import datetime
import time
from simulation.process_parameters import BaseMachineParameters
from simulation.battery_model.BaseModel import BaseModel
from simulation.helper.LocalDataSaver import LocalDataSaver
from simulation.helper.IoTHubSender import IoTHubSender


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
        self.start_datetime = None
        self.total_time = 0
        self.calculator = None
        # self.kwargs = kwargs
        # Helpers
        self.local_saver = LocalDataSaver(process_name)
        self.iot_sender = IoTHubSender(connection_string)

    @abstractmethod
    def input_model(self, previous_model: BaseModel):
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
                current_properties, self.total_time
            )
            print(f"Data saved to {path}")
        except Exception as e:
            print(f"Failed to save data to local folder: {e}")

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
        self.start_datetime = datetime.now()

    def turn_off(self):
        """Turn off the machine."""
        self.state = False
        self.total_time = 0

    def pre_run_check(self):
        """Pre-run check for the machine."""
        if self.battery_model is None:
            raise ValueError("Battery model is not set")
        if self.machine_parameters is None:
            raise ValueError("Machine parameters are not set")
        return True

    def get_current_state(self, process_specifics=None):
        """Get the current properties of the machine."""
        if self.state:
            return {
                "timestamp": datetime.now().isoformat(),
                "state": "On",
                "duration": round(self.total_time, 2),
                "process": self.process_name,
                "temperature_C": round(self.battery_model.temperature, 2) if hasattr(self.battery_model, 'temperature') else None,
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


    def run_simulation(self, total_steps=100, pause_between_steps=0.1, verbose=True):
        """Run the simulation."""
        self.turn_on()
        if verbose:
            print(f"Machine {self.process_name} is running for {total_steps} steps")
        for t in range(1, total_steps):
            self.total_time = t
            self.battery_model.update_properties(self.machine_parameters)
            if verbose:
                print(self.get_current_state())
            time.sleep(pause_between_steps)
        self.turn_off()

    # idea to standardise the step logic with decorator @abstractmethod
    #  @abstractmethod
    # def step_logic(self):
    #     """
    #     Abstract method that must be implemented by concrete machine classes.
    #     This method is called at each step of the simulation.
    #     """
    #     pass
