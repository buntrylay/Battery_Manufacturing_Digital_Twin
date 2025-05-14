import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.factory.Factory import Factory
from simulation.battery_model.Slurry import Slurry
from simulation.machine.MixingMachine import MixingMachine
from simulation.machine.CoatingMachine import CoatingMachine

# Define the mixing ratios for anode slurry components
# Ratios represent the volume fraction of each component in the final mixture
user_input_anode = {
    "PVDF": 0.05,  # 5% PVDF binder
    "CA": 0.045,   # 4.5% Conductive Additive
    "AM": 0.495,   # 49.5% Active Material
    "H2O": 0.41    # 41% H2O solvent
}

# Define the mixing ratios for cathode slurry components
user_input_cathode = {
    "PVDF": 0.013,  # 1.3% PVDF binder
    "CA": 0.039,   # 3.9% Conductive Additive
    "AM": 0.598,   # 59.8% Active Material - LNMC?
    "NMP": 0.35    # 35% H2O solvent
}

# Define the coating parameters
user_input_coating = {
    "coating_speed": 0.05,  # m/s (0,05 - 5 m/s)
    "gap_height": 200e-6, # meters (50e-6 to 300 e-6)
    "flow_rate": 5e-6,  # m³/s (Possibly fixed)
    "coating_width": 0.5  # m (possibly fixed)
}

# Create a new slurry instance for anode with 200L total volume
anode_slurry = Slurry("Anode")
cathode_slurry = Slurry("Cathode")

# Create mixing machine instances
anode_mixing_machine = MixingMachine("TK_Mix_Anode", "Anode", anode_slurry, user_input_anode)
cathode_mixing_machine = MixingMachine("TK_Mix_Cathode", "Cathode", cathode_slurry, user_input_cathode)

# Create coating machine instances
anode_coating_machine = CoatingMachine("MC_Coat_Anode", user_input_coating)
cathode_coating_machine = CoatingMachine("MC_Coat_Cathode", user_input_coating)

# Initialize the factory
factory = Factory()

# Add machines to factory with dependencies
factory.add_machine(anode_mixing_machine)  # No dependencies
factory.add_machine(cathode_mixing_machine)  # No dependencies
factory.add_machine(anode_coating_machine, 
                   dependencies=["TK_Mix_Anode"])  # Depends on anode mixer
factory.add_machine(cathode_coating_machine, 
                   dependencies=["TK_Mix_Cathode"])  # Depends on cathode mixer

# Start the simulation process
factory.start_simulation()