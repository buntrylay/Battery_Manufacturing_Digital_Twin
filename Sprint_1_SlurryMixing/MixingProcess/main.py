from Factory import Factory
from Slurry import Slurry
from Machines import MixingMachine

# Define the mixing ratios for anode slurry components
# Ratios represent the volume fraction of each component in the final mixture
user_input_anode = {
    "PVDF": 0.05,  # 5% PVDF binder
    "CA": 0.045,   # 4.5% Conductive Additive
    "AM": 0.495,   # 49.5% Active Material
    "H2O": 0.41    # 41% H2O solvent
}

# Create a new slurry instance for anode with 200L total volume
anode_slurry = Slurry("Anode")

# Initialize the factory for managing the manufacturing process
factory = Factory()

# Create a mixing machine instance for anode slurry
# Parameters:
#   - ID: "TK_Mix_Anode" (Tank Mixer for Anode)
#   - Type: "Anode"
#   - Slurry: anode_slurry instance
#   - Ratios: user_input_anode dictionary
anode_mixing_machine = MixingMachine("TK_Mix_Anode", "Anode", anode_slurry, user_input_anode)

# Add the mixing machine to the factory
factory.add_machine(anode_mixing_machine)

# Start the simulation process
factory.start_simulation()