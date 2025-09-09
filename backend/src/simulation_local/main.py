import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.factory import Batch, PlantSimulation

#Import Parameters Classes
from simulation.process_parameters.Parameters import (
    MixingParameters,
    CoatingParameters,
    DryingParameters,
    CalendaringParameters,
    SlittingParameters,
    ElectrodeInspectionParameters,
    RewindingParameters,
    ElectrolyteFillingParameters,
    FormationCyclingParameters,
    AgingParameters
)

# Import Machines from Machines Folder
from simulation.machine import (
    MixingMachine,
    CoatingMachine,
    DryingMachine,
    CalendaringMachine,
    SlittingMachine,
    ElectrodeInspectionMachine,
    RewindingMachine,
    ElectrolyteFillingMachine,
    FomationCyclingMachine,
    AgingMachine
)

# Import Models from Battery Model Folder
from simulation.battery_model import (
    MixingModel,
    CoatingModel,
    DryingModel,
    CalendaringModel,
    SlittingModel,
    ElectrodeInspectionModel,
    RewindingModel,
    ElectrolyteFillingModel,
    FormationCyclingModel,
    AgingModel
)
# Define the mixing ratios for anode slurry components
user_input_anode = {
    "PVDF": 0.05,
    "CA": 0.045,
    "AM": 0.495,
    "solvent": 0.41
}

coating_params = {
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
    "slitting_tension": 150
}

#  Electrode Inspection's input parameters 
user_input_electrode_inspection = {
    "epsilon_width_max": 0.1,  
    "epsilon_thickness_max": 10e-6,
    "B_max": 2.0,
    "D_surface_max": 3
}

rewinding_params = {
    "rewinding_speed": 0.5,
    "initial_tension": 100,
    "tapering_steps": 0.3,
    "environment_humidity": 30
}

filling_params = {
    "Vacuum_level": 100,
    "Vacuum_filling": 100,
    "Soaking_time": 10
}

formation_params = {
    "Charge_current_A": 0.05,
    "Charge_voltage_limit_V": 0.05,
    "Voltage": 4
}

aging_params = {
    "k_leak": 1e-8,
    "temperature": 25,
    "aging_time_days": 10
}

# batch_1 = Batch(id="Batch_1")
# plant_simulation = PlantSimulation()
# plant_simulation.add_batch(batch_1)
# plant_simulation.run()
anode_mixing_model = MixingModel("Anode")
anode_mixing_machine = MixingMachine("Anode_Mixer",
    anode_mixing_model,
    MixingParameters(AM=-1, CA=0.045, PVDF=0.05, solvent=0.41))
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
