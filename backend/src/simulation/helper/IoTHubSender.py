import json
from typing import Optional

try:
    from azure.iot.device import IoTHubDeviceClient, Message  # type: ignore
except Exception:  # pragma: no cover - azure is optional at runtime
    IoTHubDeviceClient = None  # type: ignore
    Message = None  # type: ignore


class IoTHubSender:
    """
    Encapsulates Azure IoT Hub client creation and message sending.
    """

    def __init__(self, connection_string: Optional[str] = None):
        self.connection_string = connection_string
        self.client = None
        if connection_string and IoTHubDeviceClient is not None:
            try:
                self.client = IoTHubDeviceClient.create_from_connection_string(connection_string)
            except Exception:
                self.client = None

    @property
    def is_configured(self) -> bool:
        return self.client is not None

    def send_json(self, data: dict) -> bool:
        """
        Send a JSON-serializable dictionary to Azure IoT Hub via MQTT.

        Returns True if sent, False otherwise.
        """
        if not self.client or Message is None:
            return False
        try:
            msg = Message(json.dumps(data))
            self.client.send_message(msg)
            return True
        except Exception:
            return False


