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
# from simulation.machine.ElectrodeRewindingMachine import ElectrodeRewindingMachine

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

#  Electrode Rewinding's input parameters - Ai Vi
# user_input_rewinding = {
#     "core_diameter": 0.2,
#     "initial_tension": 200,
#     "taper_factor": 1.0,
#     "rewind_speed": 0.5,
#     "humidity": 30
# }

# Create slurry instances
anode_slurry = Slurry("Anode")
cathode_slurry = Slurry("Cathode")

# Create mixing machines
anode_mixing_machine = MixingMachine("TK_Mix_Anode", "Anode", anode_slurry, user_input_anode)
cathode_mixing_machine = MixingMachine("TK_Mix_Cathode", "Cathode", cathode_slurry, user_input_cathode)

# Create coating machines
anode_coating_machine = CoatingMachine("MC_Coat_Anode", user_input_coating)
cathode_coating_machine = CoatingMachine("MC_Coat_Cathode", user_input_coating)

# Create drying machines
anode_drying_machine = DryingMachine("MC_Dry_Anode", web_speed= 0.01)
cathode_drying_machine = DryingMachine("MC_Dry_Cathode", web_speed= 0.01)

# ✅ Create calendaring machine
anode_calendaring_machine = CalendaringMachine("MC_Calendar_Anode", user_input_calendaring)
cathode_calendaring_machine = CalendaringMachine("MC_Calendar_Cathode", user_input_calendaring)
# Create slitting machines - Ai Vi
anode_slitting_machine = SlittingMachine("MC_Slit_Anode", user_input_slitting)

# Create electrode inspection machines - Ai Vi
anode_electrode_inspection_machine = ElectrodeInspectionMachine("MC_Inspect_Anode", user_input_electrode_inspection)

# # Create electrode rewinding - Ai Vi
# anode_electrode_rewinding_machine = ElectrodeRewindingMachine("MC_Rewind_Anode", user_input_slitting)
# Initialize factory
factory = Factory()

# Add machines to factory
factory.add_machine(anode_mixing_machine)
factory.add_machine(cathode_mixing_machine)
factory.add_machine(anode_coating_machine, dependencies=["TK_Mix_Anode"])
factory.add_machine(cathode_coating_machine, dependencies=["TK_Mix_Cathode"])
factory.add_machine(anode_drying_machine, dependencies=["MC_Coat_Anode"])
factory.add_machine(cathode_drying_machine, dependencies=["MC_Coat_Cathode"])
factory.add_machine(anode_calendaring_machine, dependencies=["MC_Dry_Anode"])
factory.add_machine(cathode_calendaring_machine, dependencies=["MC_Dry_Cathode"])   
factory.add_machine(anode_slitting_machine, dependencies=["MC_Calendar_Anode"])
# factory.add_machine(cathode_slitting_machine, dependencies=["MC_Calendar_Cathode"])
factory.add_machine(anode_electrode_inspection_machine, dependencies=["MC_Slit_Anode"])

# factory.add_machine(anode_electrode_rewinding_machine, dependencies=["MC_Inspect_Anode"])
# Start the simulation
factory.start_simulation()
