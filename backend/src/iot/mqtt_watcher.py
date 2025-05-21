import os
import time
import json
from azure.iot.device import IoTHubDeviceClient, Message

# Set your Azure IoT Hub device connection string
CONNECTION_STRING = "HostName=...;DeviceId=...;SharedAccessKey=..."

# Get absolute paths relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Directories to watch
WATCH_DIRS = [
    os.path.join(BASE_DIR, "mixing_output"),
    os.path.join(BASE_DIR, "coating_output")
]

def send_file_to_azure(file_path, client):
    with open(file_path, "r") as f:
        data = f.read()
    msg = Message(data)
    msg.content_encoding = "utf-8"
    msg.content_type = "application/json"
    client.send_message(msg)
    print(f"Sent {file_path} to Azure IoT Hub.")

def watch_and_send():
    print("Watching for new files...")
    client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)
    sent_files = set()
    try:
        while True:
            for dir in WATCH_DIRS:
                for filename in os.listdir(dir):
                    if filename.endswith(".json"):
                        full_path = os.path.join(dir, filename)
                        if full_path not in sent_files:
                            send_file_to_azure(full_path, client)
                            sent_files.add(full_path)
            time.sleep(2)  # Adjust as needed
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        client.shutdown()

if __name__ == "__main__":
    watch_and_send()