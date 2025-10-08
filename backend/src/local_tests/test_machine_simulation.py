import sys
import os
import random
import numpy as np
import pytest
from sqlalchemy import true

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from simulation.machine.MixingMachine import MixingMachine
from simulation.machine.CoatingMachine import CoatingMachine
from simulation.machine.DryingMachine import DryingMachine
from simulation.machine.CalendaringMachine import CalendaringMachine
from simulation.machine.SlittingMachine import SlittingMachine
from simulation.machine.ElectrodeInspectionMachine import ElectrodeInspectionMachine
from simulation.machine.RewindingMachine import RewindingMachine
from simulation.machine.ElectrolyteFillingMachine import ElectrolyteFillingMachine
from simulation.machine.FormationCyclingMachine import FormationCyclingMachine
from simulation.machine.AgingMachine import AgingMachine
# models
from simulation.battery_model.MixingModel import MixingModel
from simulation.battery_model.ElectrodeInspectionModel import ElectrodeInspectionModel
from simulation.battery_model.RewindingModel import RewindingModel

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
    AgingParameters,
)


@pytest.fixture(scope="module")
def mixing_setup():
    random.seed(0)
    params = MixingParameters(
        AM_ratio=0.5,
        CA_ratio=0.1,
        PVDF_ratio=0.15,
        solvent_ratio=0.25,
    )
    model = MixingModel("Anode")
    machine = MixingMachine(
        process_name="mixing",
        mixing_model=model,
        mixing_parameters=params,
    )
    machine.calculate_total_steps()
    for t in range(machine.total_steps):
        machine.step_logic(t, True)
    machine.battery_model.update_properties(params, t)
    expected_volumes = {
        "AM": machine.mixing_tank_volume * params.AM_ratio,
        "CA": machine.mixing_tank_volume * params.CA_ratio,
        "PVDF": machine.mixing_tank_volume * params.PVDF_ratio,
        "solvent": machine.mixing_tank_volume * params.solvent_ratio,
    }
    return {"machine": machine, "params": params, "expected_volumes": expected_volumes}


@pytest.fixture(scope="module")
def coating_setup(mixing_setup):
    params = CoatingParameters(
        coating_speed=0.5,
        gap_height=0.0002,
        flow_rate=2e-5,
        coating_width=0.5,
    )
    machine = CoatingMachine(
        process_name="coating",
        coating_parameters=params,
    )
    machine.receive_model_from_previous_process(mixing_setup["machine"].battery_model)
    machine.calculate_total_steps()
    machine.step_logic(0, True)
    machine.battery_model.update_properties(params)
    expected = {
        "shear_rate": params.coating_speed / params.gap_height,
        "wet_thickness": params.flow_rate
        / (params.coating_speed * params.coating_width),
    }
    return {"machine": machine, "params": params, "expected": expected}


@pytest.fixture(scope="module")
def drying_setup(coating_setup):
    params = DryingParameters(web_speed=0.5)
    machine = DryingMachine(
        process_name="drying",
        drying_parameters=params,
    )
    machine.receive_model_from_previous_process(coating_setup["machine"].battery_model)
    machine.calculate_total_steps()
    initial_solvent = machine.battery_model.calculate_initial_solvent_mass()
    for t in range(machine.total_steps):
        machine.step_logic(t, True)
    final_solvent = machine.battery_model.M_solvent
    return {
        "machine": machine,
        "params": params,
        "initial_solvent": initial_solvent,
        "final_solvent": final_solvent,
    }


@pytest.fixture(scope="module")
def calendaring_setup(drying_setup):
    drying_machine = drying_setup["machine"]
    dry_thickness = max(drying_machine.battery_model.dry_thickness, 1e-6)
    params = CalendaringParameters(
        roll_gap=5e-5,
        roll_pressure=2.2e6,
        temperature=25.0,
        roll_speed=1.0,
        dry_thickness=dry_thickness,
        initial_porosity=0.45,
    )
    machine = CalendaringMachine(
        process_name="calendaring",
        calendaring_parameters=params,
    )
    machine.receive_model_from_previous_process(drying_machine.battery_model)
    machine.calculate_total_steps()
    machine.battery_model.update_properties(params)
    return {"machine": machine, "params": params}


@pytest.fixture(scope="module")
def slitting_setup(calendaring_setup):
    params = SlittingParameters(
        blade_sharpness=8.0,
        slitting_speed=1.5,
        target_width=0.12,
        slitting_tension=120.0,
    )
    machine = SlittingMachine(
        process_name="slitting",
        slitting_parameters=params,
    )
    machine.receive_model_from_previous_process(calendaring_setup["machine"].battery_model)
    machine.calculate_total_steps()
    np.random.seed(0)
    machine.battery_model.update_properties(params)
    return {"machine": machine, "params": params}


@pytest.fixture(scope="module")
def electrode_inspection_setup(slitting_setup):
    params = ElectrodeInspectionParameters(
        epsilon_width_max=0.15,
        epsilon_thickness_max=1e-5,
        B_max=5.0,
        D_surface_max=3,
    )
    machine = ElectrodeInspectionMachine(
        process_name="electrode_inspection",
        electrode_inspection_parameters=params,
    )
    machine.receive_model_from_previous_process(slitting_setup["machine"].battery_model)
    machine.calculate_total_steps()
    np.random.seed(0)
    machine.battery_model.update_properties(params)
    return {"machine": machine, "params": params}


@pytest.fixture(scope="module")
def rewinding_setup(electrode_inspection_setup, slitting_setup):
    params = RewindingParameters(
        rewinding_speed=0.5,
        initial_tension=100.0,
        tapering_steps=0.3,
        environment_humidity=45.0,
    )
    electrode_machine = electrode_inspection_setup["machine"]
    inspection_params = electrode_inspection_setup["params"]
    slitting_machine = slitting_setup["machine"]

    np.random.seed(1)
    secondary_electrode = ElectrodeInspectionModel(slitting_machine.battery_model)
    secondary_electrode.update_properties(inspection_params)

    rewinding_model = RewindingModel(
        electrode_machine.battery_model,
        secondary_electrode,
    )
    machine = RewindingMachine(
        process_name="rewinding",
        rewinding_parameters=params,
    )
    machine.receive_model_from_previous_process(rewinding_model)
    machine.calculate_total_steps()
    machine.battery_model.update_properties(params, interval=1)
    return {"machine": machine, "params": params}


@pytest.fixture(scope="module")
def electrolyte_filling_setup(rewinding_setup):
    params = ElectrolyteFillingParameters(
        vacuum_level=90.0,
        vacuum_filling=90.0,
        soaking_time=6,
    )
    machine = ElectrolyteFillingMachine(
        process_name="electrolyte_filling",
        electrolyte_filling_parameters=params,
    )
    machine.receive_model_from_previous_process(rewinding_setup["machine"].battery_model)
    machine.calculate_total_steps()
    eta_progression = []
    for t in range(machine.total_steps):
        machine.current_time_step = t
        machine.battery_model.current_time_step = t
        machine.battery_model.update_properties(params)
        eta_progression.append(machine.battery_model.eta_wetting)
    return {
        "machine": machine,
        "params": params,
        "eta_progression": eta_progression,
    }


@pytest.fixture(scope="module")
def formation_setup(electrolyte_filling_setup):
    params = FormationCyclingParameters(
        charge_current_A=0.1,
        charge_voltage_limit_V=4.0,
        initial_voltage=3.0,
        formation_duration_s=5,
    )
    # temporary aliases so the current implementation can run
    params.Charge_current_A = params.charge_current_A
    params.Charge_voltage_limit_V = params.charge_voltage_limit_V
    params.Initial_Voltage = params.initial_voltage

    machine = FormationCyclingMachine(
        process_name="formation_cycling",
        formation_cycling_parameters=params,
    )
    machine.receive_model_from_previous_process(
        electrolyte_filling_setup["machine"].battery_model
    )
    machine.total_steps = params.formation_duration_s
    voltage_trace = []
    for t in range(machine.total_steps):
        machine.step_logic(t, True)
        voltage_trace.append(machine.battery_model.get_properties()["Voltage_V"])
        if not machine.state and t > 0:
            break
    return {"machine": machine, "params": params, "voltage_trace": voltage_trace}


@pytest.fixture(scope="module")
def aging_setup(formation_setup):
    params = AgingParameters(
        k_leak=1e-6,
        temperature=25.0,
        aging_time_days=2,
    )
    machine = AgingMachine(
        process_name="aging",
        aging_parameters=params,
    )
    machine.receive_model_from_previous_process(formation_setup["machine"].battery_model)
    machine.calculate_total_steps()
    soc_history = []
    for days in range(0, machine.total_steps, 24):
        seconds_elapsed = days * 3600
        machine.battery_model.update_properties(params, seconds_elapsed)
        soc_history.append(machine.battery_model.SOC)
    return {"machine": machine, "params": params, "soc_history": soc_history}


def test_mixing_machine_adds_expected_component_volumes(mixing_setup):
    machine = mixing_setup["machine"]
    expected = mixing_setup["expected_volumes"]
    assert machine.total_steps == 300
    assert machine.battery_model.AM == pytest.approx(expected["AM"])
    assert machine.battery_model.CA == pytest.approx(expected["CA"])
    assert machine.battery_model.PVDF == pytest.approx(expected["PVDF"])
    assert machine.battery_model.solvent == pytest.approx(expected["solvent"])


def test_coating_machine_calculates_shear_rate_and_wet_thickness(coating_setup):
    machine = coating_setup["machine"]
    expected = coating_setup["expected"]
    assert machine.total_steps == 10
    assert machine.shear_rate == pytest.approx(expected["shear_rate"])
    props = machine.battery_model.get_properties()
    assert props["wet_thickness"] == pytest.approx(expected["wet_thickness"], rel=1e-2)


def test_drying_machine_reduces_solvent_mass(drying_setup):
    machine = drying_setup["machine"]
    assert machine.total_steps == 20
    assert drying_setup["final_solvent"] <= pytest.approx(drying_setup["initial_solvent"])
    assert drying_setup["final_solvent"] >= 0


def test_calendaring_machine_updates_porosity_and_thickness(calendaring_setup):
    machine = calendaring_setup["machine"]
    params = calendaring_setup["params"]
    assert machine.total_steps == 10
    props = machine.battery_model.get_properties()
    assert props["final_thickness"] == pytest.approx(params.roll_gap)
    assert 0 < props["porosity"] < params.initial_porosity


def test_slitting_machine_generates_width_variation(slitting_setup):
    machine = slitting_setup["machine"]
    params = slitting_setup["params"]
    assert machine.total_steps == 10
    props = machine.battery_model.get_properties()
    assert abs(props["width_final"] - params.target_width) < 0.2
    assert props["burr_factor"] > 0


def test_electrode_inspection_machine_produces_overall_result(electrode_inspection_setup):
    machine = electrode_inspection_setup["machine"]
    params = electrode_inspection_setup["params"]
    assert machine.total_steps == 10
    props = machine.battery_model.get_properties()
    assert isinstance(props["Overall"], bool)
    assert abs(props["epsilon_thickness"]) <= params.epsilon_thickness_max


def test_rewinding_machine_updates_wound_metrics(rewinding_setup):
    machine = rewinding_setup["machine"]
    params = rewinding_setup["params"]
    assert machine.total_steps == 10
    props = machine.battery_model.get_properties()
    assert props["wound_length"] == pytest.approx(params.rewinding_speed)
    assert props["roll_diameter"] >= machine.battery_model.D_core


def test_electrolyte_filling_machine_improves_wetting_over_time(electrolyte_filling_setup):
    machine = electrolyte_filling_setup["machine"]
    params = electrolyte_filling_setup["params"]
    eta_progression = electrolyte_filling_setup["eta_progression"]
    assert machine.total_steps == params.soaking_time
    assert eta_progression[0] < eta_progression[-1] <= 1


def test_formation_cycling_machine_voltage_progression(formation_setup):
    machine = formation_setup["machine"]
    params = formation_setup["params"]
    voltage_trace = formation_setup["voltage_trace"]
    assert len(voltage_trace) >= 2
    assert voltage_trace[0] == pytest.approx(params.Initial_Voltage)
    assert all(v <= params.Charge_voltage_limit_V for v in voltage_trace)
    assert voltage_trace[-1] == pytest.approx(params.Charge_voltage_limit_V)


@pytest.mark.xfail(reason="calculate_total_steps currently asserts on the wrong type")
def test_formation_cycling_calculate_total_steps_known_bug(
    electrolyte_filling_setup, formation_setup
):
    params = formation_setup["params"]
    machine = FormationCyclingMachine(
        process_name="formation_cycling",
        formation_cycling_parameters=params,
    )
    machine.receive_model_from_previous_process(
        electrolyte_filling_setup["machine"].battery_model
    )
    machine.calculate_total_steps()
    assert machine.total_steps == params.formation_duration_s + 1


def test_aging_machine_soc_decay_over_time(aging_setup):
    machine = aging_setup["machine"]
    params = aging_setup["params"]
    soc_history = aging_setup["soc_history"]
    assert machine.total_steps == params.aging_time_days * 24
    assert len(soc_history) >= 2
    assert soc_history[-1] < soc_history[0]
