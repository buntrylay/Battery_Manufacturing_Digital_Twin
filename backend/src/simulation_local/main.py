import sys
import os
import threading
import json
from pathlib import Path
from simulation.factory.Factory import Factory
from simulation.battery_model.MixingModel import MixingModel
from simulation.machine.MixingMachine import MixingMachine
from simulation.machine.CoatingMachine import CoatingMachine
from simulation.machine.DryingMachine import DryingMachine
from simulation.machine.CalendaringMachine import CalendaringMachine
from simulation.machine.SlittingMachine import SlittingMachine
from simulation.machine.ElectrodeInspectionMachine import ElectrodeInspectionMachine
from simulation.machine.RewindingMachine import RewindingMachine
from simulation.machine.ElectrolyteFillingMachine import ElectrolyteFillingMachine
from simulation.machine.FomationCyclingMachine import FormationCyclingMachine
from simulation.machine.AgingMachine import AgingMachine

# -----------------------------
# Paths
# -----------------------------
RESULTS_PATH = Path("results")
RESULTS_PATH.mkdir(parents=True, exist_ok=True)

# -----------------------------
# User input parameters
# -----------------------------
mixing_ratios = {
    "Anode": {"AM": 0.495, "CA": 0.045, "PVDF": 0.05, "H2O": 0.41},
    "Cathode": {"AM": 0.598, "CA": 0.039, "PVDF": 0.013, "NMP": 0.35}
}

coating_params = {
    "coating_speed": 0.05,
    "gap_height": 200e-6,
    "flow_rate": 5e-6,
    "coating_width": 0.5
}

drying_params = {"web_speed": 0.5}

calendaring_params = {
    "roll_gap": 100e-6,
    "roll_pressure": 2e6,
    "roll_speed": 2.0,
    "dry_thickness": 150e-6,
    "initial_porosity": 0.45,
    "temperature": 25
}

slitting_params = {
    "w_input": 500,
    "blade_sharpness": 8,
    "slitting_speed": 1.5,
    "target_width": 100,
    "slitting_tension": 150
}

inspection_params = {
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

# -----------------------------
# Factory setup
# -----------------------------
factory = Factory()
machines = {}

for etype in ["Anode", "Cathode"]:
    # 1. Mixing
    mixing_model = MixingModel(etype)
    mix_machine = MixingMachine(
        machine_id=f"TK_Mix_{etype}",
        electrode_type=etype,
        mixing_model=mixing_model,
        ratios=mixing_ratios[etype]
    )
    factory.add_machine(mix_machine)
    machines[f"{etype}_Mixing"] = mix_machine

    # 2. Coating
    coating_machine = CoatingMachine(
        machine_id=f"MC_Coat_{etype}",
        user_input=coating_params
    )
    factory.add_machine(coating_machine, dependencies=[f"TK_Mix_{etype}"])
    machines[f"{etype}_Coating"] = coating_machine

    # 3. Drying
    drying_machine = DryingMachine(
        machine_id=f"MC_Dry_{etype}",
        web_speed=drying_params["web_speed"]
    )
    factory.add_machine(drying_machine, dependencies=[f"MC_Coat_{etype}"])
    machines[f"{etype}_Drying"] = drying_machine

    # 4. Calendaring
    calendaring_machine = CalendaringMachine(
        machine_id=f"MC_Cal_{etype}",
        user_input=calendaring_params
    )
    factory.add_machine(calendaring_machine, dependencies=[f"MC_Dry_{etype}"])
    machines[f"{etype}_Calendaring"] = calendaring_machine

    # 5. Slitting
    slitting_machine = SlittingMachine(
        machine_id=f"MC_Slit_{etype}",
        user_input=slitting_params
    )
    factory.add_machine(slitting_machine, dependencies=[f"MC_Cal_{etype}"])
    machines[f"{etype}_Slitting"] = slitting_machine

    # 6. Inspection
    inspection_machine = ElectrodeInspectionMachine(
        machine_id=f"MC_Inspect_{etype}",
        user_input=inspection_params
    )
    factory.add_machine(inspection_machine, dependencies=[f"MC_Slit_{etype}"])
    machines[f"{etype}_Inspection"] = inspection_machine

    # 7. Rewinding
    rewinding_machine = RewindingMachine(
        machine_id=f"MC_Rewind_{etype}",
        user_input=rewinding_params
    )
    factory.add_machine(rewinding_machine, dependencies=[f"MC_Inspect_{etype}"])
    machines[f"{etype}_Rewinding"] = rewinding_machine

    # 8. Electrolyte Filling
    filling_machine = ElectrolyteFillingMachine(
        machine_id=f"MC_Filling_{etype}",
        user_input=filling_params
    )
    factory.add_machine(filling_machine, dependencies=[f"MC_Rewind_{etype}"])
    machines[f"{etype}_Electrolyte_Filling"] = filling_machine

    # 9. Formation Cycling
    formation_machine = FormationCyclingMachine(
        machine_id=f"MC_Formation_{etype}",
        user_input=formation_params
    )
    factory.add_machine(formation_machine, dependencies=[f"MC_Filling_{etype}"])
    machines[f"{etype}_Formation_Cycling"] = formation_machine

    # 10. Aging
    aging_machine = AgingMachine(
        machine_id=f"MC_Aging_{etype}",
        user_input=aging_params
    )
    factory.add_machine(aging_machine, dependencies=[f"MC_Formation_{etype}"])
    machines[f"{etype}_Aging"] = aging_machine

# -----------------------------
# Start factory simulation
# -----------------------------
factory.start_simulation()

# Wait for all threads to complete
for t in factory.threads:
    t.join()

# -----------------------------
# Save final results
# -----------------------------
for etype in ["Anode", "Cathode"]:
    machine = machines[f"{etype}_Mixing"]  # You can choose any machine to get final result
    final_result = machine._format_result(is_final=True)
    result_file = RESULTS_PATH / f"{etype}_result.json"
    with open(result_file, "w") as f:
        json.dump(final_result, f, indent=4)

print("✅ Full simulation completed. Results saved in 'results/' folder.")
