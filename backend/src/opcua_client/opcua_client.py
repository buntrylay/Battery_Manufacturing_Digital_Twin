import asyncio
import json
from asyncua import Client, ua
from azure.iot.device.aio import IoTHubDeviceClient
from azure.iot.device import Message

OPCUA_ENDPOINT = "opc.tcp://localhost:4840/freeopcua/server/"
IOTHUB_CONNECTION_STRING = "HostName=SW-DEV-a633d6e2-a3f2-11ef-a7f3-000d3a8201a5.azure-devices.net;DeviceId=ACTestSwin;SharedAccessKey=AIZ4O/jiLzaXY4v5GMr5VSPfA26TF4o14iNApHMv3VA="

MACHINE_IDS = ["TK_Mix_Anode", "TK_Mix_Cathode"]  # Update with your actual machine IDs

class DataChangeHandler:
    def __init__(self, iothub_client, machine_id):
        self.iothub_client = iothub_client
        self.machine_id = machine_id

    async def datachange_notification(self, node, val, data):
        print(f"[{self.machine_id}] OPC UA value changed: {val}")
        # Optionally, wrap the value in a JSON object with machine_id
        payload = json.dumps({"machine_id": self.machine_id, "result": val})
        msg = Message(payload)
        await self.iothub_client.send_message(msg)
        print(f"[{self.machine_id}] Sent data to Azure IoT Hub.")

async def main():
    # Connect to Azure IoT Hub
    iothub_client = IoTHubDeviceClient.create_from_connection_string(IOTHUB_CONNECTION_STRING)
    await iothub_client.connect()

    # Connect to OPC UA server
    async with Client(OPCUA_ENDPOINT) as opcua_client:
        print("Connected to OPC UA server.")
        objects = opcua_client.nodes.objects

        # Subscribe to each MixingMachine's LatestResult variable
        handler_tasks = []
        for machine_id in MACHINE_IDS:
            machine_node = await objects.get_child([f"2:{machine_id}"])
            var_node = await machine_node.get_child(["2:LatestResult"])
            handler = DataChangeHandler(iothub_client, machine_id)
            sub = await opcua_client.create_subscription(100, handler)
            await sub.subscribe_data_change(var_node)
            handler_tasks.append(sub)

        print("Subscribed to OPC UA variables. Waiting for data changes...")
        try:
            while True:
                await asyncio.sleep(1)
        finally:
            for sub in handler_tasks:
                await sub.delete()
            await iothub_client.shutdown()

if __name__ == "__main__":
    asyncio.run(main())