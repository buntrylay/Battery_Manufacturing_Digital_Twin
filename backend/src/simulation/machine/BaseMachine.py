from abc import ABC, abstractmethod
from azure.iot.device import IoTHubDeviceClient, Message
import json
from metrics.metrics import set_machine_status

class BaseMachine(ABC):
    """
    Abstract base class representing a generic machine in the battery manufacturing process.
    
    Attributes:
        id (str): Unique identifier for the machine
        is_on (bool): Current operational status of the machine
        calculator (SlurryPropertyCalculator): Calculator for slurry properties
    """
    
    def __init__(self, id, connection_string=None):
        """
        Initialise a new Machine instance.
        
        Args:
            id (str): Unique identifier for the machine
        """
        self.id = id
        self.is_on = False
        self.calculator = None
        self.connection_string = connection_string
        self.iot_client = None
        if connection_string:
            try:
                self.iot_client = IoTHubDeviceClient.create_from_connection_string(connection_string)
            except Exception as e:
                print(f"Failed to create IoT Hub client: {e}")

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

    @abstractmethod
    def run(self, dependencies_result=None):
        """
        Main execution logic for the machine.
        It sets the machine status metric before and after running the subclass logic.
        """
        try:
            # Report status as 'running' (1) to Prometheus
            set_machine_status(self.id, 1)

            # This is a placeholder for the actual simulation logic
            # that will be implemented in each specific machine (like MixingMachine, etc.)
            # Your original code likely had an abstract method or a 'pass' here,
            # which is correct. The key is wrapping it.

            print(f"[{self.id}] Child machine logic should be running now.")

        except Exception as e:
            print(f"Error in machine {self.id}: {e}")
        finally:
            # This block runs whether the machine succeeded or failed
            self.completed.set()
            # Report status as 'completed/idle' (0) to Prometheus
            set_machine_status(self.id, 0)
            print(f"Completed {self.id}")