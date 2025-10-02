"""
Test script to verify parameter class consistency with user inputs.

This script tests that all parameter classes can be instantiated with
the user input data from simulation_local/main.py
"""

from simulation.process_parameters import (
    MixingParameters, CoatingParameters, DryingParameters,
    CalendaringParameters, SlittingParameters, ElectrodeInspectionParameters,
    RewindingParameters, ElectrolyteFillingParameters, FormationCyclingParameters,
    AgingParameters
)


def test_mixing_parameters():
    """Test MixingParameters with user input data."""
    print("Testing MixingParameters...")
    
    # Anode mixing parameters
    anode_params = MixingParameters(AM_ratio=0.495, CA_ratio=0.045, PVDF_ratio=0.05, solvent_ratio=0.41)
    anode_params.validate_parameters()
    print("✓ Anode mixing parameters valid")
    
    # Cathode mixing parameters (note: NMP vs solvent)
    cathode_params = MixingParameters(AM_ratio=0.598, CA_ratio=0.039, PVDF_ratio=0.013, solvent_ratio=0.35)
    cathode_params.validate_parameters()
    print("✓ Cathode mixing parameters valid")
    
    print(f"  Anode params: {anode_params.get_parameters_dict()}")
    print(f"  Cathode params: {cathode_params.get_parameters_dict()}")


def test_coating_parameters():
    """Test CoatingParameters with user input data."""
    print("\nTesting CoatingParameters...")
    
    coating_params = CoatingParameters(
        coating_speed=0.05,
        gap_height=200e-6,
        flow_rate=5e-6,
        coating_width=0.5
    )
    coating_params.validate_parameters()
    print("✓ Coating parameters valid")
    print(f"  Coating params: {coating_params.get_parameters_dict()}")


def test_drying_parameters():
    """Test DryingParameters with user input data."""
    print("\nTesting DryingParameters...")
    
    drying_params = DryingParameters(
        wet_thickness=100e-6,
        solid_content=0.5,
        web_speed=0.5
    )
    drying_params.validate_parameters()
    print("✓ Drying parameters valid")
    print(f"  Drying params: {drying_params.get_parameters_dict()}")


def test_calendaring_parameters():
    """Test CalendaringParameters with user input data."""
    print("\nTesting CalendaringParameters...")
    
    calendaring_params = CalendaringParameters(
        roll_gap=100e-6,
        roll_pressure=2e6,
        temperature=25,
        roll_speed=2.0,
        dry_thickness=150e-6,
        initial_porosity=0.45
    )
    calendaring_params.validate_parameters()
    print("✓ Calendaring parameters valid")
    print(f"  Calendaring params: {calendaring_params.get_parameters_dict()}")


def test_slitting_parameters():
    """Test SlittingParameters with user input data."""
    print("\nTesting SlittingParameters...")
    
    slitting_params = SlittingParameters(
        blade_sharpness=8,
        slitting_speed=1.5,
        target_width=100,
        slitting_tension=150
    )
    slitting_params.validate_parameters()
    print("✓ Slitting parameters valid")
    print(f"  Slitting params: {slitting_params.get_parameters_dict()}")


def test_electrode_inspection_parameters():
    """Test ElectrodeInspectionParameters with user input data."""
    print("\nTesting ElectrodeInspectionParameters...")
    
    inspection_params = ElectrodeInspectionParameters(
        epsilon_width_max=0.1,
        epsilon_thickness_max=10e-6,
        B_max=2.0,
        D_surface_max=3
    )
    inspection_params.validate_parameters()
    print("✓ Electrode inspection parameters valid")
    print(f"  Inspection params: {inspection_params.get_parameters_dict()}")


def test_rewinding_parameters():
    """Test RewindingParameters with user input data."""
    print("\nTesting RewindingParameters...")
    
    rewinding_params = RewindingParameters(
        rewinding_speed=0.5,
        initial_tension=100,
        tapering_steps=0.3,
        environment_humidity=30
    )
    rewinding_params.validate_parameters()
    print("✓ Rewinding parameters valid")
    print(f"  Rewinding params: {rewinding_params.get_parameters_dict()}")


def test_electrolyte_filling_parameters():
    """Test ElectrolyteFillingParameters with user input data."""
    print("\nTesting ElectrolyteFillingParameters...")
    
    elec_filling_params = ElectrolyteFillingParameters(
        Vacuum_level=100,
        Vacuum_filling=100,
        Soaking_time=10
    )
    elec_filling_params.validate_parameters()
    print("✓ Electrolyte filling parameters valid")
    print(f"  Electrolyte filling params: {elec_filling_params.get_parameters_dict()}")


def test_formation_cycling_parameters():
    """Test FormationCyclingParameters with user input data."""
    print("\nTesting FormationCyclingParameters...")
    
    formation_params = FormationCyclingParameters(
        Charge_current_A=0.05,
        Charge_voltage_limit_V=0.05,
        Voltage=4
    )
    formation_params.validate_parameters()
    print("✓ Formation cycling parameters valid")
    print(f"  Formation cycling params: {formation_params.get_parameters_dict()}")


def test_aging_parameters():
    """Test AgingParameters with user input data."""
    print("\nTesting AgingParameters...")
    
    aging_params = AgingParameters(
        k_leak=1e-8,
        temperature=25,
        aging_time_days=10
    )
    aging_params.validate_parameters()
    print("✓ Aging parameters valid")
    print(f"  Aging params: {aging_params.get_parameters_dict()}")


def test_invalid_parameters():
    """Test parameter validation with invalid data."""
    print("\nTesting parameter validation with invalid data...")
    
    # Test invalid mixing parameters (ratios don't sum to 1)
    try:
        invalid_mixing = MixingParameters(AM_ratio=0.5, CA_ratio=0.1, PVDF_ratio=0.1, solvent_ratio=0.1)
        invalid_mixing.validate_parameters()
        print("✗ Invalid mixing parameters should have failed")
    except ValueError as e:
        print(f"✓ Invalid mixing parameters correctly failed: {e}")
    
    # Test invalid coating parameters (negative speed)
    try:
        invalid_coating = CoatingParameters(
            coating_speed=-0.05,
            gap_height=200e-6,
            flow_rate=5e-6,
            coating_width=0.5
        )
        invalid_coating.validate_parameters()
        print("✗ Invalid coating parameters should have failed")
    except ValueError as e:
        print(f"✓ Invalid coating parameters correctly failed: {e}")
    
    # Test invalid drying parameters (solid_content > 1)
    try:
        invalid_drying = DryingParameters(
            wet_thickness=100e-6,
            solid_content=1.5,  # Invalid: > 1
            web_speed=0.5
        )
        invalid_drying.validate_parameters()
        print("✗ Invalid drying parameters should have failed")
    except ValueError as e:
        print(f"✓ Invalid drying parameters correctly failed: {e}")


def main():
    """Run all parameter consistency tests."""
    print("Parameter Consistency Test")
    print("=" * 40)
    
    test_mixing_parameters()
    test_coating_parameters()
    test_drying_parameters()
    test_calendaring_parameters()
    test_slitting_parameters()
    test_electrode_inspection_parameters()
    test_rewinding_parameters()
    test_electrolyte_filling_parameters()
    test_formation_cycling_parameters()
    test_aging_parameters()
    test_invalid_parameters()
    
    print("\n" + "=" * 40)
    print("All parameter consistency tests completed!")


if __name__ == "__main__":
    main()
