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
from simulation.machine.ElectrolyteFillingMachine import ElectrolyteFillingMachine
from simulation.machine.FomationCyclingMachine import FormationCyclingMachine
from simulation.machine.AgingMachine import AgingMachine

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
# Create calendaring machines
anode_calendaring_machine = CalendaringMachine("MC_Calendar_Anode", user_input_calendaring)
cathode_calendaring_machine = CalendaringMachine("MC_Calendar_Cathode", user_input_calendaring)
# Create slitting machine
slitting_machine = SlittingMachine("MC_Slit", user_input_slitting)
# Create electrode inspection machine
electrode_inspection_machine = ElectrodeInspectionMachine("MC_Inspect", user_input_electrode_inspection)
# Create rewinding machine
rewinding_machine = RewindingMachine("MC_Rewind", user_input_rewinding)
# Create electrolyte filling machine
electrolyte_filling_machine = ElectrolyteFillingMachine("MC_ElecFill", user_input_elec_filling)
# Create formation cycling machine
formation_machine = FormationCyclingMachine("MC_Formation", user_input_formation)
# Create aging machine
aging_machine = AgingMachine("MC_Aging", user_input_aging)

# Initialize factory with new pipeline structure
factory = Factory()

# Add machines to anode line
factory.add_machine(anode_mixing_machine, 'anode', 'mixing')
factory.add_machine(anode_coating_machine, 'anode', 'coating')
factory.add_machine(anode_drying_machine, 'anode', 'drying')
factory.add_machine(anode_calendaring_machine, 'anode', 'calendaring')

# Add machines to cathode line
factory.add_machine(cathode_mixing_machine, 'cathode', 'mixing')
factory.add_machine(cathode_coating_machine, 'cathode', 'coating')
factory.add_machine(cathode_drying_machine, 'cathode', 'drying')
factory.add_machine(cathode_calendaring_machine, 'cathode', 'calendaring')

# Add machines to merged line (after calendaring)
factory.add_machine(slitting_machine, 'merged', 'slitting')
factory.add_machine(electrode_inspection_machine, 'merged', 'inspection')
factory.add_machine(rewinding_machine, 'merged', 'rewinding')
factory.add_machine(electrolyte_filling_machine, 'merged', 'electrolyte_filling')
factory.add_machine(formation_machine, 'merged', 'formation_cycling')
factory.add_machine(aging_machine, 'merged', 'aging')

# Start the simulation
print("Starting Battery Manufacturing Pipeline Simulation...")
factory.start_simulation()