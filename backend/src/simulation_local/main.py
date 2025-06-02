import sys
import os
import asyncio
import threading

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.factory.Factory import Factory
from simulation.battery_model.Slurry import Slurry
from simulation.machine.MixingMachine import MixingMachine
from simulation.machine.CoatingMachine import CoatingMachine
from simulation.machine.CalendaringMachine import CalendaringMachine
from simulation.machine.DryingMachine import DryingMachine 
from simulation.machine.SlittingMachine import SlittingMachine
from simulation.machine.ElectrodeInspectionMachine import ElectrodeInspectionMachine
from simulation.machine.RewindingMachine import RewindingMachine
from opcua_server.MixingOPCUAServer import MixingOPCUAServer

MIXING_MACHINE_IDS = ["TK_Mix_Anode", "TK_Mix_Cathode"]
opcua_server = MixingOPCUAServer()
opcua_loop = asyncio.new_event_loop()

def start_opcua_server():
    asyncio.set_event_loop(opcua_loop)
    opcua_loop.run_until_complete(opcua_server.setup(MIXING_MACHINE_IDS))
    opcua_loop.run_until_complete(opcua_server.run())

opcua_thread = threading.Thread(target=start_opcua_server, daemon=True)
opcua_thread.start()


# Define the mixing ratios for anode slurry components
user_input_anode = {
    "PVDF": 0.05,
    "CA": 0.045,
    "AM": 0.495,
    "H2O": 0.41
}

# Define the mixing ratios for cathode slurry components
user_input_cathode = {
    "PVDF": 0.013,
    "CA": 0.039,
    "AM": 0.598,
    "NMP": 0.35
}

# Create slurry instances
anode_slurry = Slurry("Anode")
cathode_slurry = Slurry("Cathode")

# Create mixing machines
anode_mixing_machine = MixingMachine("TK_Mix_Anode", "Anode", anode_slurry, user_input_anode, opcua_server)
cathode_mixing_machine = MixingMachine("TK_Mix_Cathode", "Cathode", cathode_slurry, user_input_cathode, opcua_server)

for machine in [anode_mixing_machine, cathode_mixing_machine]:
    machine.opcua_loop = opcua_loop

# Initialize factory
factory = Factory()

# Add machines to factory
factory.add_machine(anode_mixing_machine)
factory.add_machine(cathode_mixing_machine)

input("Start the opcua_client gateway now, then press Enter to continue...")

# Start the simulation
factory.start_simulation()