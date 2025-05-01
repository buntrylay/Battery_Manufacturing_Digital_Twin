import ssl
import json
import time
import paho.mqtt.client as mqtt

from SASTokenHelper import generate_sas_token

class AzureMQTTClient:
    def __init__(self, iot_hub_name, device_id, sas_token):
        self.iot_hub_name = iot_hub_name
        self.device_id = device_id
        self.sas_token = sas_token

        self.endpoint = f"{self.iot_hub_name}.azure-devices.net"
        self.username = f"{self.endpoint}/{self.device_id}/?api-version=2021-04-12"
        self.client_id = self.device_id
        self.topic = f"devices/{self.device_id}/messages/events/"

        self.client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv311)
        self.client.username_pw_set(self.username, password=self.sas_token)
        self.client.tls_set_context(ssl.create_default_context())

    def connect(self):
        self.client.connect(self.endpoint, port=8883)
        self.client.loop_start()

    def send_json(self, payload: dict):
        json_data = json.dumps(payload)
        result = self.client.publish(self.topic, json_data)
        status = result[0]
        if status == mqtt.MQTT_ERR_SUCCESS:
            print(f"[✓] Sent to Azure IoT Hub: {json_data}")
        else:
            print(f"[!] Failed to send message: {status}")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

if __name__ == "__main__":
    IOT_HUB_NAME = "your-hub"
    DEVICE_ID = "your-device-id"
    DEVICE_KEY = "your-device-key"
    SAS_TOKEN = generate_sas_token(f"{IOT_HUB_NAME}.azure-devices.net/devices/{DEVICE_ID}", DEVICE_KEY)

    mqtt_client = AzureMQTTClient(IOT_HUB_NAME, DEVICE_ID, SAS_TOKEN)
    mqtt_client.connect()

    try:
        while True:
            simulated_data = {
                "device_id": DEVICE_ID,
                "temperature": 22.5,
                "timestamp": time.time()
            }
            mqtt_client.send_json(simulated_data)
            time.sleep(5)
    except KeyboardInterrupt:
        mqtt_client.disconnect()
