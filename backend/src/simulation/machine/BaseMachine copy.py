from abc import ABC, abstractmethod
from azure.iot.device import IoTHubDeviceClient, Message
import json, threading, os
from datetime import datetime, timedelta

class BaseMachine(ABC):
    """
    Abstract base class representing a generic machine in the battery manufacturing process.
    
    Attributes:
        id (str): Unique identifier for the machine
        is_on (bool): Current operational status of the machine
        calculator (SlurryPropertyCalculator): Calculator for slurry properties
    """
    
    def __init__(self, id, process_name, connection_string=None):
        """
        Initialise a new Machine instance.
        
        Args:
            id (str): Unique identifier for the machine
        """
        self.id = id
        self.process_name = process_name
        self.is_on = False
        self.calculator = None
        self.start_datetime = datetime.now()
        self.total_time = 0
        self.lock = threading.Lock()

        self.output_dir = self.create_output_dir()

        self.connection_string = connection_string
        self.iot_client = None
        if connection_string:
            try:
                self.iot_client = IoTHubDeviceClient.create_from_connection_string(connection_string)
            except Exception as e:
                print(f"Failed to create IoT Hub client: {e}")

    def create_output_dir(self):
        dir_name = f"{self.process_name.lower()}_output"
        path = os.path.join(os.getcwd(), dir_name)
        os.makedirs(path, exist_ok=True)
        print(f"Output directory created at: {path}")
        return path

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
                print(f"Sent data to IoT Hub for machine {self.id}")
            except Exception as e:
                print(f"Failed to send data to IoT Hub: {e}")
        else:
            print("IoT Hub client not initialized.")

    def turn_on(self):
        """Turn on the machine."""
        self.is_on = True

    def turn_off(self):
        """Turn off the machine."""
        self.is_on = False

    def format_base_result(self):
        return {
            "TimeStamp": (self.start_datetime + timedelta(seconds=self.total_time)).isoformat(),
            "Duration": round(self.total_time, 5),
            "Machine ID": self.id,
            "Process": self.process_name,
            
            "Temperature (C)": round(self.ref_temperature, 2)
        }

    @abstractmethod
    def format_specific_result(self, is_final=False) -> dict:
        # each machine implements its own specific result formatting
        pass

    def format_result(self, is_final=False):
        # merge base and machine-specific results into one dict
        result = self.format_base_result()
        result.update(self.format_specific_result(is_final=is_final))
        return result

    def write_json(self, data: dict, filename_prefix="result"):
        try:
            timestamp = data["TimeStamp"].replace(":", "-").replace(".", "-")
            filename = f"{self.id}_{timestamp}_{filename_prefix}.json"
            filepath = os.path.join(self.output_dir, filename)

            with self.lock:
                with open(filepath, "w") as f:
                    json.dump(data, f, indent=4)

            print(f"Results saved to {filepath}")
            return filepath
        except Exception as e:
            print(f"Error writing result to file for {self.id}: {e}")
            return None

    @abstractmethod
    def get_output(self) -> dict:
        """Return machine output in a standard dict format."""
        pass

    @abstractmethod
    def update_from_input(self, data: dict):
        """Update machine state from dependency output."""
        pass

    @abstractmethod
    def run(self):
        """Abstract method that must be implemented by concrete machine classes."""
        pass

