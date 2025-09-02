from simulation.process_parameters.MixingParameters import MixingParameters
from simulation.battery_model.BaseModel import BaseModel


class MixingModel(BaseModel):
    """
    A class representing a battery slurry mixture containing active material (AM),
    conductive additive (CA), PVDF binder, and solvent (H2O or NMP).

    Attributes:
        total_volume (float): The target total volume of the slurry
        AM (float): Amount of active material in the slurry
        CA (float): Amount of conductive additive in the slurry
        PVDF (float): Amount of PVDF binder in the slurry
        H2O (float): Amount of solvent for anode slurry
        NMP (float): Amount of solvent for cathode slurry
    """

    def __init__(self, electrode_type):
        """
        Initialise a new MixingModel instance.

        Args:
            electrode_type (str): The type of electrode ("Anode" or "Cathode")
        """
        self.AM = 0  # Active Material volume
        self.CA = 0  # Conductive Additive volume
        self.PVDF = 0  # PVDF Binder volume
        self.solvent = 0  # Solvent volume
        self.electrode_type = electrode_type
        if electrode_type == "Anode":
            self.solvent_type = "H2O"
        elif self.electrode_type == "Cathode":
            self.solvent_type = "NMP"
        # Computed properties (Outputs)
        self.viscosity = 0  # mixing model's viscosity (Pa.s)
        self.density = 0  # mixing model's density (kg/m^3)
        self.yield_stress = 0  # mixing model's yield stress (Pa)

    def add(self, component, amount):
        """
        Add a specified amount of a component to the slurry.

        Args:
            component (str): The component to add ('AM', 'CA', 'PVDF', or 'H2O' or 'NMP')
            amount (float): The amount of the component to add
        """
        setattr(self, component, getattr(self, component) + amount)

    def calculate_density(
        self, AM_volume, CA_volume, PVDF_volume, solvent_volume, electrode_type
    ):
        """Calculate density using component volumes and densities"""

        if electrode_type == "Anode":
            RHO = {"AM": 2.26, "CA": 1.8, "PVDF": 1.17, "solvent": 1.0}
        elif electrode_type == "Cathode":
            RHO = {"AM": 2.11, "CA": 1.8, "PVDF": 1.78, "solvent": 1.03}

        total_mass = sum(
            [
                AM_volume * RHO["AM"],
                CA_volume * RHO["CA"],
                PVDF_volume * RHO["PVDF"],
                solvent_volume * RHO["solvent"],
            ]
        )

        volume = AM_volume + CA_volume + PVDF_volume + solvent_volume
        return total_mass / volume if volume > 0 else 0

    def calculate_viscosity(
        self,
        AM_volume,
        CA_volume,
        PVDF_volume,
        solvent_volume,
        max_solid_fraction=0.63,
        intrinsic_viscosity=3,
    ):
        """Calculate viscosity using Krieger-Dougherty model"""
        total_volume = AM_volume + CA_volume + PVDF_volume + solvent_volume
        solid_volume = AM_volume + CA_volume + PVDF_volume
        phi = solid_volume / total_volume if total_volume > 0 else 0

        if phi >= max_solid_fraction:
            phi = max_solid_fraction - 0.001

        return (1 - (phi / max_solid_fraction)) ** (
            -intrinsic_viscosity * max_solid_fraction
        ) * 0.017

    def calculate_yield_stress(
        self, AM_volume, CA_volume, PVDF_volume, solvent_volume, electrode_type
    ):
        """Calculate yield stress using weighted component masses"""
        if electrode_type == "Anode":
            RHO = {"AM": 2.26, "CA": 1.8, "PVDF": 1.17, "solvent": 1.0}
            WEIGHTS = {"a": 0.85, "b": 2.2, "c": 0.3, "s": -0.4}
        elif electrode_type == "Cathode":
            RHO = {"AM": 2.11, "CA": 1.8, "PVDF": 1.78, "solvent": 1.03}
            WEIGHTS = {"a": 0.9, "b": 2.5, "c": 0.3, "s": -0.5}

        return (
            WEIGHTS["a"] * AM_volume * RHO["AM"]
            + WEIGHTS["b"] * PVDF_volume * RHO["PVDF"]
            + WEIGHTS["c"] * CA_volume * RHO["CA"]
            + WEIGHTS["s"] * solvent_volume * RHO["solvent"]
        )

    def update_properties(self, machine_parameters: MixingParameters):
        """Update all computed properties"""
        self.density = self.calculate_density(
            self.AM, self.CA, self.PVDF, self.solvent, self.electrode_type
        )
        self.viscosity = self.calculate_viscosity(
            self.AM, self.CA, self.PVDF, self.solvent
        )
        self.yield_stress = self.calculate_yield_stress(
            self.AM, self.CA, self.PVDF, self.solvent, self.electrode_type
        )

    def get_total_volume(self, AM_volume, CA_volume, PVDF_volume, solvent_volume):
        """
        Calculate the current total volume of all components in the slurry.

        Returns:
            float: The sum of all components (AM + CA + PVDF + H2O or NMP)
        """
        return AM_volume + CA_volume + PVDF_volume + solvent_volume

    def get_properties(self):
        return {
            "AM_volume": round(self.AM, 4),
            "CA_volume": round(self.CA, 4),
            "PVDF_volume": round(self.PVDF, 4),
            f"{self.solvent_type}_volume": round(self.solvent, 4),
            "viscosity": round(self.viscosity, 4),
            "density": round(self.density, 4),
            "yield_stress": round(self.yield_stress, 4),
            "total_volume": round(sum([self.AM, self.CA, self.PVDF, self.solvent]), 4),
        }
