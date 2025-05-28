from typing import Dict, Any
from simulation.state.base_state import BaseBatteryState
from simulation.state.electrode_type import ElectrodeType


class Slurry(BaseBatteryState):
    def __init__(self, timestamp: int, electrode_type: ElectrodeType):
        super().__init__(timestamp)
        # self.AM_ratio: float = 0.0 (excl. because it is related to the machine parameters)
        # self.CA_ratio: float = 0.0 (excl. because it is related to the machine parameters)
        # self.PVDF_ratio: float = 0.0 (excl. because it is related to the machine parameters)
        # self.solvent_ratio: float = 0.0 (excl. because it is related to the machine parameters)

        self.solvent_type: str = ("H2O" if electrode_type == ElectrodeType.Anode else "NMP")
        self.AM: float = 0.0  # refers to the volume of active material
        self.CA: float = 0.0  # refers to the volume of conductive additive
        self.PVDF: float = 0.0  # refers to the volume of binder
        self.solvent: float = 0.0  # refers to the volume of solvent
        
        # calculated properties
        self.viscosity: float = 0.0
        self.density: float = 0.0
        self.yield_stress: float = 0.0


    def as_dict(self) -> Dict[str, Any]:
        """Convert slurry state to dictionary."""
        return {
            # slurry ratios
            "AM": self.AM,
            "CA": self.CA,
            "PVDF": self.PVDF,
            f"{self.solvent_type}": self.solvent,
            # physical properties
            "viscosity": self.viscosity,
            "density": self.density,
            "yield_stress": self.yield_stress,
        }


    def update_properties(self, viscosity: float, density: float, yield_stress: float) -> None:
        """Update the physical properties of the slurry."""
        self.viscosity = viscosity
        self.density = density
        self.yield_stress = yield_stress

    def add(self, component: str, amount: float) -> None:
        """Add component to the slurry."""
        if hasattr(self, component):
            current_value = getattr(self, component)
            setattr(self, component, current_value + amount)
        else:
            raise ValueError(f"Unknown component: {component}")
        
        