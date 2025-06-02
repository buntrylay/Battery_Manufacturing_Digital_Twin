import asyncio
from asyncua import ua, Server

class MixingOPCUAServer:
    def __init__(self, endpoint="opc.tcp://0.0.0.0:4840/freeopcua/server/"):
        self.endpoint = endpoint
        self.server = Server()
        self.machine_vars = {}

    async def setup(self, machine_ids):
        await self.server.init()
        self.server.set_endpoint(self.endpoint)
        uri = "http://battery.digital.twin"
        idx = await self.server.register_namespace(uri)
        objects = self.server.nodes.objects

        for machine_id in machine_ids:
            node = await objects.add_object(idx, machine_id)
            var = await node.add_variable(idx, "LatestResult", "")
            await var.set_writable()
            self.machine_vars[machine_id] = var

    async def set_machine_result(self, machine_id, result_json):
        var = self.machine_vars.get(machine_id)
        if var:
            await var.write_value(result_json)

    async def run(self):
        async with self.server:
            print("OPC UA AsyncIO Server started.")
            while True:
                await asyncio.sleep(1)