"""
Parameter mapping utilities to translate between frontend field names and backend parameter objects.
This module handles the conversio        backend_params = {}
        
        # Get the field mappings for this specific machine type
        if machine_type not in cls.FIELD_MAPPINGS:
            raise ValueError(f"Unknown machine type: {machine_type}")
        
        machine_field_mappings = cls.FIELD_MAPPINGS[machine_type]
        
        for frontend_field, value in frontend_data.items():
            if frontend_field in machine_field_mappings:
                backend_param = machine_field_mappings[frontend_field]
                # Convert string values to appropriate types
                if isinstance(value, str) and value.strip():
                    try:
                        backend_params[backend_param] = float(value)
                    except ValueError:
                        raise ValueError(f"Invalid value for {frontend_field}: {value}")
                elif isinstance(value, (int, float)):
                    backend_params[backend_param] = float(value)-friendly frontend names and the structured 
parameter classes expected by the simulation backend.
"""

import os
import sys

# Add the path to the simulation module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.process_parameters import (
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


class ParameterMapper:
    """Handles mapping between frontend field names and backend parameter objects."""
    
    # Define mapping from frontend field names to backend parameter names
    # Structured by machine type to avoid conflicts with duplicate field names
    FIELD_MAPPINGS = {
        "mixing": {
            "Anode PVDF": "PVDF_ratio",
            "Anode CA": "CA_ratio", 
            "Anode AM": "AM_ratio",
            "Anode Solvent": "solvent_ratio",
            "Cathode PVDF": "PVDF_ratio",
            "Cathode CA": "CA_ratio",
            "Cathode AM": "AM_ratio", 
            "Cathode Solvent": "solvent_ratio",
        },
        "coating": {
            "Coating Speed": "coating_speed",
            "Gap Height": "gap_height",
            "Flow Rate": "flow_rate",
            "Coating Width": "coating_width",
        },
        "drying": {
            "Web Speed": "web_speed",
        },
        "calendaring": {
            "Roll Gap": "roll_gap",
            "Roll Pressure": "roll_pressure",
            "Temperature": "temperature",
            "Roll Speed": "roll_speed",
            "Dry Thickness": "dry_thickness", 
            "Initial Porosity": "initial_porosity",
        },
        "slitting": {
            "Blade Sharpness": "blade_sharpness",
            "Slitting Speed": "slitting_speed",
            "Target Width": "target_width",
            "Slitting Tension": "slitting_tension",
        },
        "inspection": {
            "Width Tolerance": "epsilon_width_max",
            "Thickness Tolerance": "epsilon_thickness_max",
            "B Max": "B_max",
            "Defects Allowed": "D_surface_max",
        },
        "rewinding": {
            "Rewinding Speed": "rewinding_speed",
            "Initial Tension": "initial_tension",
            "Tapering Steps": "tapering_steps",
            "Environment Humidity": "environment_humidity",
        },
        "electrolyte_filling": {
            "Vacuum Level": "vacuum_level",
            "Vacuum Filling": "vacuum_filling",
            "Soaking Time": "soaking_time",
        },
        "formation_cycling": {
            "Charge Current": "charge_current_A",
            "Voltage": "charge_voltage_limit_V", 
            "Initial Voltage": "initial_voltage",
        },
        "aging": {
            "Leak Rate": "k_leak",
            "Temperature": "temperature",
            "Aging Days": "aging_time_days",
        }
    }
    
    # Map machine stages to parameter classes
    PARAMETER_CLASSES = {
        "mixing": MixingParameters,
        "coating": CoatingParameters,
        "drying": DryingParameters,
        "calendaring": CalendaringParameters,
        "slitting": SlittingParameters,
        "inspection": ElectrodeInspectionParameters,
        "rewinding": RewindingParameters,
        "electrolyte_filling": ElectrolyteFillingParameters,
        "formation_cycling": FormationCyclingParameters,
        "aging": AgingParameters,
    }
    
    # Map frontend stage names to backend machine IDs
    STAGE_TO_MACHINE_MAP = {
        "Anode Mixing": ("anode", "mixing"),
        "Cathode Mixing": ("cathode", "mixing"),
        "Anode Coating": ("anode", "coating"),
        "Cathode Coating": ("cathode", "coating"),
        "Anode Drying": ("anode", "drying"),
        "Cathode Drying": ("cathode", "drying"),
        "Anode Calendaring": ("anode", "calendaring"),
        "Cathode Calendaring": ("cathode", "calendaring"),
        "Anode Slitting": ("anode", "slitting"),
        "Cathode Slitting": ("cathode", "slitting"),
        "Anode Inspection": ("anode", "inspection"),
        "Cathode Inspection": ("cathode", "inspection"),
        "Rewinding": ("cell", "rewinding"),
        "Electrolyte Filling": ("cell", "electrolyte_filling"),
        "Formation Cycling": ("cell", "formation_cycling"),
        "Aging": ("cell", "aging"),
    }

    @classmethod
    def frontend_to_backend_parameters(cls, frontend_data: dict, machine_type: str) -> dict:
        """
        Convert frontend field names and values to backend parameter dictionary.
        
        Args:
            frontend_data: Dictionary with frontend field names as keys
            machine_type: The type of machine (mixing, coating, etc.)
            
        Returns:
            Dictionary with backend parameter names and values
        """
        backend_params = {}
        
        # Get the field mappings for this specific machine type
        if machine_type not in cls.FIELD_MAPPINGS:
            raise ValueError(f"Unknown machine type: {machine_type}")
        
        machine_field_mappings = cls.FIELD_MAPPINGS[machine_type]
        
        for frontend_field, value in frontend_data.items():
            if frontend_field in machine_field_mappings:
                backend_param = machine_field_mappings[frontend_field]
                # Convert string values to appropriate types
                if isinstance(value, str) and value.strip():
                    try:
                        backend_params[backend_param] = float(value)
                    except ValueError:
                        raise ValueError(f"Invalid value for {frontend_field}: {value}")
                elif isinstance(value, (int, float)):
                    backend_params[backend_param] = float(value)
        
        return backend_params


    @classmethod
    def create_parameter_object(cls, backend_params: dict, machine_type: str):
        """
        Create a parameter object from backend parameter dictionary.
        
        Args:
            backend_params: Dictionary with backend parameter names
            machine_type: The type of machine
            
        Returns:
            Instance of the appropriate parameter class
        """
        if machine_type not in cls.PARAMETER_CLASSES:
            raise ValueError(f"Unknown machine type: {machine_type}")
        
        param_class = cls.PARAMETER_CLASSES[machine_type]
        
        try:
            # Create instance and validate
            param_instance = param_class(**backend_params)
            param_instance.validate_parameters()
            return param_instance
        except TypeError as e:
            raise ValueError(f"Missing required parameters for {machine_type}: {e}")
        except Exception as e:
            raise ValueError(f"Parameter validation failed for {machine_type}: {e}")

    @classmethod
    def stage_to_machine_info(cls, stage_name: str) -> tuple:
        """
        Convert frontend stage name to backend line_type and machine_id.
        
        Args:
            stage_name: Frontend stage name (e.g., "Anode Mixing")
            
        Returns:
            Tuple of (line_type, machine_id)
        """
        if stage_name not in cls.STAGE_TO_MACHINE_MAP:
            raise ValueError(f"Unknown stage: {stage_name}")
        
        return cls.STAGE_TO_MACHINE_MAP[stage_name]

    @classmethod
    def validate_frontend_parameters(cls, frontend_data: dict, stage_name: str) -> dict:
        """
        Validate frontend parameters and return the errors if any.
        
        Args:
            frontend_data: Dictionary with frontend field names and values
            stage_name: Frontend stage name
            
        Returns:
            Dictionary with validation results
        """
        try:
            line_type, machine_id = cls.stage_to_machine_info(stage_name)
            backend_params = cls.frontend_to_backend_parameters(frontend_data, machine_id)
            
            # Handle empty parameters case
            if not backend_params:
                return {
                    "valid": True,
                    "line_type": line_type,
                    "machine_id": machine_id,
                    "parameters": None,
                    "message": "No parameters to validate (empty input)"
                }
            
            param_obj = cls.create_parameter_object(backend_params, machine_id)
            
            return {
                "valid": True,
                "line_type": line_type,
                "machine_id": machine_id,
                "parameters": param_obj,
                "message": "Parameters validated successfully"
            }
        except Exception as e:
            return {
                "valid": False,
                "error": str(e),
                "message": f"Validation failed: {e}"
            }