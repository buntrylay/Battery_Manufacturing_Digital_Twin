from simulation.calc.mixing_property_calculator import MixingPropertyCalculator
from simulation.machine.machine import Machine
from simulation.process.mixing_process import MixingProcess
from simulation.state.slurry import Slurry, ElectrodeType
from simulation.state.slurry import ElectrodeType

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
anode_slurry = Slurry(timestamp=0, electrode_type=ElectrodeType.Anode)
cathode_slurry = Slurry(timestamp=0, electrode_type=ElectrodeType.Cathode)

# Create a new mixing simulation instance for anode
anode_mixing_simulation = MixingProcess(
    id="anode_mixing",
    machine=Machine(
        id="anode_mixing",
        parameters={
            "mixing_tank_volume": 200,
            "simulation_time": 100,
        }
    ),
    calculator=MixingPropertyCalculator(ElectrodeType.Anode),
    electrode_type=ElectrodeType.Anode,
)