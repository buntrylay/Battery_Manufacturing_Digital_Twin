from typing import Dict, Any
from .process_calculator import ProcessCalculator
from ..state.electrode_type import ElectrodeType


class MixingPropertyCalculator(ProcessCalculator):
    """
    A calculator class for determining various physical properties of battery slurry.

    This class calculates important slurry properties such as density, viscosity, and yield stress
    based on the composition and physical properties of the slurry components.

    Attributes:
        RHO (dict): Dictionary of density values for each component (g/cm³)
        WEIGHTS (dict): Dictionary of weight coefficients for yield stress calculation
    """

    def __init__(self, electrode_type: ElectrodeType):
        """
        Initialize a new MixingPropertyCalculator instance.

        Args:
            electrode_type (str): Type of electrode ("Anode" or "Cathode")
        """
        if electrode_type == ElectrodeType.Anode:  # Anode
            self.RHO = {"AM": 2.26, "CA": 1.8, "PVDF": 1.17, "H2O": 1.0}
            self.WEIGHTS = {"a": 0.85, "b": 2.2, "c": 0.3, "s": -0.4}
        else:  # Cathode
            self.RHO = {"AM": 2.11, "CA": 1.8, "PVDF": 1.78, "NMP": 1.03}
            self.WEIGHTS = {"a": 0.9, "b": 2.5, "c": 0.3, "s": -0.5}

    def calculate_properties(self, state_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate all slurry properties based on component ratios.

        Args:
            state_data (Dict[str, Any]): Dictionary containing component volumes and other state data

        Returns:
            Dict[str, Any]: Dictionary containing calculated properties
        """
        return {
            "viscosity": MixingPropertyCalculator.calculate_viscosity(
                state_data["AM"],
                state_data["CA"],
                state_data["PVDF"],
                state_data["solvent"],
                self.WEIGHTS,
            ),
            "density": MixingPropertyCalculator.calculate_density(
                state_data["AM"],
                state_data["CA"],
                state_data["PVDF"],
                state_data["solvent"],
                self.RHO,
                self.electrode_type == ElectrodeType.Anode,
            ),
            "yield_stress": MixingPropertyCalculator.calculate_yield_stress(
                state_data["AM"],
                state_data["CA"],
                state_data["PVDF"],
                state_data["solvent"],
                self.RHO,
                self.WEIGHTS,
                self.electrode_type == ElectrodeType.Anode,
            ),
        }

    @staticmethod
    def calculate_density(
        am_volume: float,
        ca_volume: float,
        pvdf_volume: float,
        solvent_volume: float,
        component_densities: Dict[str, float],
        is_anode: bool,
    ) -> float:
        """
        Calculate the density of the slurry.

        The density is calculated as the total mass divided by total volume,
        where mass is the product of component volume and its density.

        Args:
            am_volume (float): Volume of active material
            ca_volume (float): Volume of conductive additive
            pvdf_volume (float): Volume of PVDF binder
            solvent_volume (float): Volume of solvent (H2O or NMP)
            component_densities (Dict[str, float]): Dictionary of density values for each component
            is_anode (bool): Whether this is an anode slurry

        Returns:
            float: The calculated density in g/cm³, or 0 if total volume is 0
        """
        total_mass = (
            am_volume * component_densities["AM"]
            + ca_volume * component_densities["CA"]
            + pvdf_volume * component_densities["PVDF"]
            + solvent_volume
            * (component_densities["H2O"] if is_anode else component_densities["NMP"])
        )
        total_volume = am_volume + ca_volume + pvdf_volume + solvent_volume
        return total_mass / total_volume if total_volume else 0

    @staticmethod
    def calculate_viscosity(
        am_volume: float,
        ca_volume: float,
        pvdf_volume: float,
        solvent_volume: float,
        max_solid_fraction: float = 0.63,
        intrinsic_viscosity: float = 3,
    ) -> float:
        """
        Calculate the viscosity of the slurry using the Krieger-Dougherty model.

        The viscosity is calculated based on the solid fraction (phi) and follows
        the Krieger-Dougherty equation: η = (1 - φ/φm)^(-[η]φm)

        Args:
            am_volume (float): Volume of active material
            ca_volume (float): Volume of conductive additive
            pvdf_volume (float): Volume of PVDF binder
            solvent_volume (float): Volume of solvent (H2O or NMP)
            max_solid_fraction (float): Maximum packing fraction (default: 0.63)
            intrinsic_viscosity (float): Intrinsic viscosity parameter (default: 3)

        Returns:
            float: The calculated viscosity in Pa·s
        """
        total_volume = am_volume + ca_volume + pvdf_volume + solvent_volume
        solid_volume = am_volume + ca_volume + pvdf_volume

        # Calculate solid fraction
        phi = solid_volume / total_volume if total_volume else 0

        # Cap solid fraction to prevent infinite viscosity
        if phi >= max_solid_fraction:
            phi = max_solid_fraction - 0.001

        # Apply Krieger-Dougherty equation with scaling factor of 2
        return (1 - (phi / max_solid_fraction)) ** (
            -intrinsic_viscosity * max_solid_fraction
        ) * 0.017

    @staticmethod
    def calculate_yield_stress(
        am_volume: float,
        ca_volume: float,
        pvdf_volume: float,
        h2o_volume: float,
        nmp_volume: float,
        component_densities: Dict[str, float],
        weight_coefficients: Dict[str, float],
        is_anode: bool,
    ) -> float:
        """
        Calculate the yield stress of the slurry.

        The yield stress is calculated as a weighted sum of the masses of different
        components, where each component's contribution is weighted by its respective
        coefficient from the weight coefficients.

        Args:
            am_volume (float): Volume of active material
            ca_volume (float): Volume of conductive additive
            pvdf_volume (float): Volume of PVDF binder
            h2o_volume (float): Volume of H2O solvent
            nmp_volume (float): Volume of NMP solvent
            component_densities (Dict[str, float]): Dictionary of density values for each component
            weight_coefficients (Dict[str, float]): Dictionary of weight coefficients for yield stress calculation
            is_anode (bool): Whether this is an anode slurry

        Returns:
            float: The calculated yield stress in Pa
        """
        # Calculate component masses
        am_mass = am_volume * component_densities["AM"]
        ca_mass = ca_volume * component_densities["CA"]
        pvdf_mass = pvdf_volume * component_densities["PVDF"]
        solvent_mass = (
            h2o_volume * component_densities["H2O"]
            if is_anode
            else nmp_volume * component_densities["NMP"]
        )

        # Calculate weighted sum of component masses
        return (
            weight_coefficients["a"] * am_mass  # Active Material contribution
            + weight_coefficients["b"] * pvdf_mass  # PVDF Binder contribution
            + weight_coefficients["c"] * ca_mass  # Conductive Additive contribution
            + weight_coefficients["s"] * solvent_mass
        )  # Solvent contribution
