import threading
from simulation.battery_model import CollectorFoil
from simulation.battery_model.Slurry import Slurry
from simulation.machine import CoatingMachineForNow
from simulation.machine.MixingMachine import MixingMachine

def run_machine(machine):
    machine.turn_on()
    machine.run()
    machine.turn_off()

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
    "PVDF": 0.013, # 1.3% PVDF binder
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

anode_mixing_machine = MixingMachine("TK_Mix_Anode", "Anode", anode_slurry, user_input_anode)
cathode_mixing_machine = MixingMachine("TK_Mix_Cathode", "Cathode", cathode_slurry, user_input_cathode)

anode_mix_thread = threading.Thread(target=run_machine, args=(anode_mixing_machine,))
cathode_mix_thread = threading.Thread(target=run_machine, args=(cathode_mixing_machine,))

anode_mix_thread.start()
cathode_mix_thread.start()

anode_mix_thread.join()
cathode_mix_thread.join()

print(f"anode_slurry.density: {anode_slurry.density} and anode_slurry.viscosity: {anode_slurry.viscosity}")
print(f"cathode_slurry.density: {cathode_slurry.density} and cathode_slurry.viscosity: {cathode_slurry.viscosity}")
anode_collector_foil = CollectorFoil(anode_slurry)
cathode_collector_foil = CollectorFoil(cathode_slurry)

anode_coating_machine = CoatingMachineForNow("MC_Coat_Anode", anode_collector_foil, user_input_coating)
cathode_coating_machine = CoatingMachineForNow("MC_Coat_Cathode", cathode_collector_foil, user_input_coating)

anode_coating_thread = threading.Thread(target=run_machine, args=(anode_coating_machine,))
cathode_coating_thread = threading.Thread(target=run_machine, args=(cathode_coating_machine,))

anode_coating_thread.start()
cathode_coating_thread.start()

anode_coating_thread.join()
cathode_coating_thread.join()

print("Simulation finished")