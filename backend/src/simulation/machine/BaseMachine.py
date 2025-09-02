from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
import os
from azure.iot.device import IoTHubDeviceClient, Message
import json
from simulation.battery_model.BaseModel import BaseModel

class BaseMachine(ABC):
    """
    Abstract base class representing a generic machine in the battery manufacturing process.
    
    Attributes:
        id (str): Unique identifier for the machine
        is_on (bool): Current operational status of the machine
        calculator (SlurryPropertyCalculator): Calculator for slurry properties
    """
    
    def __init__(self, process_name, battery_model: BaseModel, machine_parameters: dataclass, connection_string=None, **kwargs):
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
        self.kwargs = kwargs
        # Save data to file related properties
        self.output_dir = os.path.join(os.getcwd(), f"{process_name.lower()}_output")
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory created at: {self.output_dir}")
        # IoT Hub
        self.connection_string = connection_string
        self.iot_client = None
        if connection_string:
            try:
                self.iot_client = IoTHubDeviceClient.create_from_connection_string(connection_string)
            except Exception as e:
                print(f"Failed to create IoT Hub client: {e}")

    # delegate to a different class
    def send_json_to_iothub(self, data):
        """
        Send a JSON-serializable dictionary to Azure IoT Hub via MQTT.

        Args:
            data (dict): The data to send.
        """
        if self.iot_client:
            try:
                msg = Message(json.dumps(data))
                self.iot_client.send_message(msg)
                print(f"Sent data to IoT Hub for machine {self.process_name}")
            except Exception as e:
                print(f"Failed to send data to IoT Hub: {e}")
        else:
            print("IoT Hub client not initialised.")

    # delegate to a different class
    def save_data_to_local_folder(self):
        """
        Save data to a local folder.
        """
        try:
            current_properties = self.get_current_properties()
            print(current_properties)
            timestamp = current_properties["timestamp"].replace(":", "-").replace(".", "-")
            unique_filename = f"{self.process_name.lower()}_output/{self.process_name.lower()}_{timestamp}_result_at_{round(self.total_time)}s.json"
            with open(unique_filename, "w") as f:
                json.dump(current_properties, f)
            print(f"Data saved to {unique_filename}")
        except Exception as e:
            print(f"Failed to save data to local folder: {e}")

    # delegate to a different class
    def save_all_results(self, results):
        """
        Save all results to a local folder.
        """
        try:
            with open(os.path.join(self.output_dir, f"{self.process_name.lower()}_summary.json"), "w") as f:
                json.dump(results, f)
            print(f"Summary of all results saved to {self.output_dir}")
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

#new method to get current properties of each machine
    def get_current_properties(self, process_specifics=None):
        """Get the current properties of the machine."""
        return {
            "timestamp": datetime.now().isoformat(),
            "duration": round(self.total_time, 2),
            "process": self.process_name,
            "temperature_C": round(self.battery_model.temperature, 2) if hasattr(self.battery_model, 'temperature') else None,
            "battery_model": self.battery_model.get_properties(),
            "machine_parameters": asdict(self.machine_parameters),
            "process_specifics": process_specifics,
        }
    
    # idea to standardise the step logic with decorator @abstractmethod
    #  @abstractmethod
    # def step_logic(self):
    #     """
    #     Abstract method that must be implemented by concrete machine classes.
    #     This method is called at each step of the simulation.
    #     """
    #     pass

    @abstractmethod
    def run(self):
        """Abstract method that must be implemented by concrete machine classes."""
        pass