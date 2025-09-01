import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.machine.CoatingMachine import CoatingMachine, CoatingParameters
from simulation.battery_model.CoatingModel import CoatingModel
from simulation.battery_model.MixingModel import MixingModel
from simulation.machine.MixingMachine import MaterialRatios, MixingMachine, MixingParameters

# Define the mixing ratios for anode slurry components
user_input_anode = {
    "PVDF": 0.05,
    "CA": 0.045,
    "AM": 0.495,
    "solvent": 0.41
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

# Define calendaring parameters
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

# Electrolyte Filling's input parameters
user_input_elec_filling = {
    "Vacuum_level" : 100,
    "Vacuum_filling" : 100,
    "Soaking_time" : 10
}

# Formation Cycling's input parameters
user_input_formation = {
    "Charge_current_A" : 0.05,
    "Charge_voltage_limit_V" : 0.05,
    "Voltage": 4
}

# Aging's input parameters
user_input_aging = {
    "k_leak": 1e-8,
    "temperature": 25,
    "aging_time_days": 10
}

anode_mixing_model = MixingModel("Anode")
anode_mixing_machine = MixingMachine(anode_mixing_model, MixingParameters(MaterialRatios(AM=0.495, CA=0.045, PVDF=0.05, solvent=0.41)))
anode_mixing_machine.run()
# __init__() CoatingModel
coating_model = CoatingModel(anode_mixing_model)
anode_coating_machine = CoatingMachine(coating_model, CoatingParameters(coating_speed=0.05, gap_height=200e-6, flow_rate=5e-6, coating_width=0.5))
anode_coating_machine.run()