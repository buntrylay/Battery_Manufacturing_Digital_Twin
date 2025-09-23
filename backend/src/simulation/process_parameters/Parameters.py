from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
import math

# All public class parameters wihtin this file
__all__ = [
    'BaseMachineParameters',
    'MixingParameters',
    'CoatingParameters',
    'DryingParameters',
    'CalendaringParameters',
    'SlittingParameters',
    'ElectrodeInspectionParameters',
    'RewindingParameters',
    'ElectrolyteFillingParameters',
    'FormationCyclingParameters',
    'AgingParameters'
]


# Abstract Base Class
@dataclass
class BaseMachineParameters(ABC):
    @abstractmethod
    def validate_parameters(self):
        pass

    @abstractmethod
    def get_parameters_dict(self):
        pass
    def __post_init__(self):
        """
        Automatically calls the validation logic right after any subclass is created.
        """
        self.validate_parameters()

# Parameter implementations

@dataclass
class MixingParameters(BaseMachineParameters):
    AM: float
    CA: float
    PVDF: float
    solvent: float
    
    def validate_parameters(self):
        if self.AM < 0 or self.CA < 0 or self.PVDF < 0 or self.solvent < 0:
            raise ValueError("Material ratios cannot be negative.")
        
        ratio_sum = self.AM + self.CA + self.PVDF + self.solvent
        if not math.isclose(ratio_sum, 1.0):
            raise ValueError(f"The sum of material ratios must be 1, but it was {ratio_sum}")
    
    def get_parameters_dict(self):
        return asdict(self)


@dataclass
class CoatingParameters(BaseMachineParameters):
    coating_speed: float
    gap_height: float
    flow_rate: float
    coating_width: float

    def validate_parameters(self):
        if self.coating_speed <= 0:
            raise ValueError("Coating speed must be greater than 0")
        if self.gap_height <= 0:
            raise ValueError("Gap height must be greater than 0")
        if self.flow_rate <= 0:
            raise ValueError("Flow rate must be greater than 0")
        if self.coating_width <= 0:
            raise ValueError("Coating width must be greater than 0")

    def get_parameters_dict(self):
        return asdict(self)



@dataclass
class DryingParameters:
    V_air: float
    T_dry: float
    H_air: float
    drying_length: float
    web_speed: float
    coating_width: float = 0.5
    h_air: float = 0.1
    density: float = 1500
    solvent_density: float = 800
    delta_t: float = 1
    max_safe_evap_rate: float = 0.004

    def validate_parameters(self):
        if self.V_air <= 0:
            raise ValueError("Air velocity must be positive.")
        if self.T_dry <= 0:
            raise ValueError("Drying temperature must be positive.")
        if self.H_air < 0 or self.H_air > 1:
            raise ValueError("Relative humidity must be between 0 and 1.")
        if self.drying_length <= 0:
            raise ValueError("Drying length must be positive.")
        if self.web_speed <= 0:
            raise ValueError("Web speed must be positive.")
        if self.coating_width <= 0:
            raise ValueError("Coating width must be positive.")
        if self.h_air <= 0:
            raise ValueError("Heat transfer coefficient must be positive.")
        if self.density <= 0:
            raise ValueError("Density must be positive.")
        if self.solvent_density <= 0:
            raise ValueError("Solvent density must be positive.")
        if self.delta_t <= 0:
            raise ValueError("Time step must be positive.")
        if self.max_safe_evap_rate <= 0:
            raise ValueError("Max safe evaporation rate must be positive.")
    
    def get_parameters_dict(self):
        return asdict(self)

@dataclass
class CalendaringParameters(BaseMachineParameters):
    roll_gap: float
    roll_pressure: float
    temperature: float
    roll_speed: float
    dry_thickness: float
    initial_porosity: float

    def validate_parameters(self):
        if self.roll_gap <= 0:
            raise ValueError("Roll gap must be positive.")
        if self.roll_pressure <= 0:
            raise ValueError("Roll pressure must be positive.")
        if self.roll_speed <= 0:
            raise ValueError("Roll speed must be positive.")
        if not (0 < self.initial_porosity < 1):
            raise ValueError("Initial porosity must be between 0 and 1.")
        if self.dry_thickness <= 0:
            raise ValueError("Dry thickness must be positive.")
        
    def get_parameters_dict(self):
        return asdict(self)


@dataclass
# initialize parameters
class SlittingParameters(BaseMachineParameters):
    blade_sharpness: float
    slitting_speed: float
    target_width: float
    slitting_tension: float

    def validate_parameters(self):
        if self.blade_sharpness <= 0:
            raise ValueError("Blade Value must eb greater than 0")
        if self.slitting_speed <= 0:
            raise ValueError("Slitting speed must be greater than 0")
        if self.target_width <= 0:
            raise ValueError("Target width must be greater than 0")
        if self.slitting_tension <= 0:
            raise ValueError("Slitting tension must be greater than 0")
    def get_parameters_dict(self):
        return asdict(self)

    
@dataclass
class ElectrodeInspectionParameters(BaseMachineParameters):
    epsilon_width_max: float
    epsilon_thickness_max: float
    B_max: float
    D_surface_max: float

    def validate_parameters(self):
        if self.epsilon_width_max <= 0:
            raise ValueError("Epsilon width max must be greater than 0")
        if self.epsilon_thickness_max <= 0:
            raise ValueError("Epsilon thickness max must be greater than 0")
        if self.B_max <= 0:
            raise ValueError("B max must be greater than 0")
        if self.D_surface_max <= 0:
            raise ValueError("D surface max must be greater than 0")

    def get_parameters_dict(self):
        return asdict(self)

@dataclass
class RewindingParameters:
    rewinding_speed: float
    initial_tension: float
    tapering_steps: float
    environment_humidity: float

    def validate_parameters(self):
        if self.rewinding_speed <= 0:
            raise ValueError("Rewinding speed must be greater than 0")
        if self.initial_tension <= 0:
            raise ValueError("Initial tension must be greater than 0")
        if self.tapering_steps < 0:
            raise ValueError("Tapering steps must be non-negative")
        if not (0 <= self.environment_humidity <= 1):
            raise ValueError("Environment humidity must be between 0 and 1")

    def get_parameters_dict(self):
        return asdict(self)

@dataclass
class ElectrolyteFillingParameters:
    vacuum_level: float
    vacuum_filling : float
    soaking_time: float

    def validate_parameters(self):
        if self.vacuum_level <= 0:
            raise ValueError("Vacuum level must be greater than 0")
        if self.vacuum_filling <= 0:
            raise ValueError("Vacuum filling must be greater than 0")
        if self.soaking_time <= 0:
            raise ValueError("Soaking time must be greater than 0")

    def get_parameters_dict(self):
        return asdict(self)

@dataclass
class FormationCyclingParameters:
    charge_current_A: float
    charge_voltage_limit_V: float
    voltage: float          
    formation_duration_s: int = 200 # can be adjusted based on real process time

    def validate_parameters(self):
        if charge_current_A <= 0:
            raise ValueError("Charge current must be greater than 0")
        if charge_voltage_limit_V <= 0:
            raise ValueError("Charge voltage limit must be greater than 0")
        if voltage <= 0:
            raise ValueError("Voltage must be greater than 0")
        if formation_duration_s <= 0:
            raise ValueError("Formation duration must be greater than 0")

    def get_parameters_dict(self):
        return asdict(self)

@dataclass
class AgingParameters:
    k_leak : float
    temperature: float
    aging_time_days: float

    def validate_parameters(self):
        if self.k_leak <= 0:
            raise ValueError("k_leak must be greater than 0")
        if self.temperature <= 0:
            raise ValueError("Temperature must be greater than 0")
        if self.aging_time_days <= 0:
            raise ValueError("Aging time (days) must be greater than 0")
    
    def get_parameters_dict(self):
        return asdict(self)
