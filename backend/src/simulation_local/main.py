import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.machine.CoatingMachine import CoatingMachine, CoatingParameters
from simulation.battery_model.CoatingModel import CoatingModel
from simulation.machine.MixingMachine import MaterialRatios, MixingMachine, MixingParameters
from simulation.battery_model.MixingModel import MixingModel
from simulation.machine.DryingMachine import DryingMachine, DryingParameters
from simulation.battery_model.DryingModel import DryingModel
from simulation.machine.CalendaringMachine import CalendaringMachine, CalendaringParameters
from simulation.battery_model.CalendaringModel import CalendaringModel
from simulation.machine.SlittingMachine import SlittingMachine, SlittingParameters
from simulation.battery_model.SlittingModel import SlittingModel
from simulation.machine.ElectrodeInspectionMachine import ElectrodeInspectionMachine, ElectrodeInspectionParameters
from simulation.battery_model.ElectrodeInspectionModel import ElectrodeInspectionModel
from simulation.machine.RewindingMachine import RewindingMachine, RewindingParameters
from simulation.battery_model.RewindingModel import RewindingModel
from simulation.machine.ElectrolyteFillingMachine import ElectrolyteFillingMachine, ElectrolyteFillingParameters
from simulation.battery_model.ElectrolyteFillingModel import ElectrolyteFillingModel
from simulation.machine.FomationCyclingMachine import FormationCyclingMachine, FormationCyclingParameters
from simulation.battery_model.FormationCyclingModel import FormationCyclingModel
from simulation.machine.AgingMachine import AgingMachine, AgingParameters
from simulation.battery_model.AgingModel import AgingModel
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

# Define drying parameters


# Define calendaring parameters
user_input_calendaring = {
    "roll_gap": 100e-6,             # meters
    "roll_pressure": 2e6,           # Pascals
    "roll_speed": 2.0,              # m/s
    "dry_thickness": 150e-6,        # From coating (m)
    "initial_porosity": 0.45,       # Assumed porosity after drying
    "temperature": 25               # Optional
}

#  Slitting's input parameters 
user_input_slitting = {
    "w_input": 500, # not in need!!!
    "blade_sharpness": 8,
    "slitting_speed": 1.5, 
    "target_width": 100,
    "slitting_tension": 150,
}

#  Electrode Inspection's input parameters 
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
drying_model = DryingModel(coating_model)
anode_drying_machine = DryingMachine(drying_model, DryingParameters(V_air=1.0, T_dry=100, H_air=80, drying_length=10, web_speed=0.5))
anode_drying_machine.run()

calendaring_model = CalendaringModel(drying_model, initial_porosity=0.45)
anode_calendaring_machine = CalendaringMachine(calendaring_model, CalendaringParameters(roll_gap = 100e-6, roll_pressure = 2e6, roll_speed = 2.0, dry_thickness = 150e-6, initial_porosity= 0.45, temperature =25))
anode_calendaring_machine.run()

slitting_model = SlittingModel(calendaring_model)
anode_slitting_machine = SlittingMachine(slitting_model, SlittingParameters(blade_sharpness=8, slitting_speed=1.5, target_width=100, slitting_tension=150))
anode_slitting_machine.run()

electrode_inspection_model = ElectrodeInspectionModel(slitting_model)
electrode_inspection_machine = ElectrodeInspectionMachine(electrode_inspection_model, ElectrodeInspectionParameters(epsilon_width_max=0.1, epsilon_thickness_max=10e-6, B_max=2.0, D_surface_max=3))
electrode_inspection_machine.run()

rewinding_model = RewindingModel(electrode_inspection_model)    
rewinding_machine = RewindingMachine(rewinding_model, RewindingParameters(rewinding_speed=0.5, initial_tension=100, tapering_steps=0.3, environment_humidity=30))
rewinding_machine.run()

elec_filling_model = ElectrolyteFillingModel(rewinding_model)
elec_filling_machine = ElectrolyteFillingMachine(elec_filling_model, ElectrolyteFillingParameters(Vacuum_level=100, Vacuum_filling=100, Soaking_time=10))
elec_filling_machine.run()

formation_model = FormationCyclingModel(elec_filling_model)
formation_machine = FormationCyclingMachine(formation_model, FormationCyclingParameters(Charge_current_A=0.05, Charge_voltage_limit_V=0.05, Voltage=4))
formation_machine.run()

aging_model = AgingModel(formation_model)
aging_machine = AgingMachine(aging_model, AgingParameters(k_leak=1e-8, temperature=25, aging_time_days=10))
aging_machine.run()