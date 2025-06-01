import sys
import os

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

# Define the coating parameters
user_input_coating = {
    "coating_speed": 0.05,
    "gap_height": 200e-6,
    "flow_rate": 5e-6,
    "coating_width": 0.5
}

# ✅ Define calendaring parameters
user_input_calendaring = {
    "roll_gap": 100e-6,             # meters
    "roll_pressure": 2e6,           # Pascals
    "roll_speed": 2.0,              # m/s
    "dry_thickness": 150e-6,        # From coating (m)
    "initial_porosity": 0.45,       # Assumed porosity after drying
    "temperature": 25               # Optional
}
#  Slitting's input parameters - Ai Vi
user_input_slitting = {
    "w_input": 500,
    "blade_sharpness": 8,
    "slitting_speed": 1.5, 
    "target_width": 100,
    "slitting_tension": 150,
}

#  Electrode Inspection's input parameters - Ai Vi
user_input_electrode_inspection = {
    "epsilon_width_max": 0.1,  
    "epsilon_thickness_max": 10e-6,
    "B_max": 2.0,
    "D_surface_max": 3
}

#  Rewinding's input parameters
user_input_rewinding = {
    "rewinding_speed": 0.5,  # m/s
    "initial_tension": 100,       # N
    "tapering_steps": 0.3, # meters
    "environment_humidity": 30    # %
}
# Create slurry instances
anode_slurry = Slurry("Anode")
cathode_slurry = Slurry("Cathode")

# Create mixing machines
anode_mixing_machine = MixingMachine("TK_Mix_Anode", "Anode", anode_slurry, user_input_anode, "HostName=SW-DEV-a633d6e2-a3f2-11ef-a7f3-000d3a8201a5.azure-devices.net;DeviceId=ACTestSwin;SharedAccessKey=AIZ4O/jiLzaXY4v5GMr5VSPfA26TF4o14iNApHMv3VA=")
cathode_mixing_machine = MixingMachine("TK_Mix_Cathode", "Cathode", cathode_slurry, user_input_cathode, "")

# Initialize factory
factory = Factory()

# Add machines to factory
factory.add_machine(anode_mixing_machine)

# Start the simulation
factory.start_simulation()