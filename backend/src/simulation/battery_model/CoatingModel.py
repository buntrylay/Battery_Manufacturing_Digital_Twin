from simulation.process_parameters.Parameters import CoatingParameters
from simulation.battery_model.MixingModel import MixingModel
from simulation.battery_model.BaseModel import BaseModel


class CoatingModel(BaseModel):
    def __init__(self, mixing_model: MixingModel):
        # passed from mixing model
        total_solids = (
            mixing_model.AM + mixing_model.CA + mixing_model.PVDF
        )  # total solids volume, taken from mixing model's AM, CA, PVDF
        total_volume = (
            total_solids + mixing_model.solvent
        )  # total volume, taken from mixing model's AM, CA, PVDF, solvent
        self.electrode_type = mixing_model.electrode_type
        self.solid_content = total_solids / total_volume if total_volume > 0 else 0
        self.viscosity = mixing_model.viscosity  # taken from mixing model's viscosity
        # calculated properties
        self.wet_thickness = 0  # wet thickness (m)
        self.dry_thickness = 0  # dry thickness (m)
        self.defect_risk = False  # defect risk (bool)

    def calculate_wet_thickness(self, flow_rate, coating_speed, coating_width):
        """
        Calculate the wet coating thickness based on mass balance.

        This calculation assumes a uniform flow distribution across the coating width.
        The wet thickness is determined by the ratio of flow rate to the product of
        coating speed and width.

        Args:
            flow_rate (float): Volumetric flow rate in m³/s
            coating_speed (float): Speed of the coating process in m/s
            coating_width (float): Width of the coating in m

        Returns:
            float: Wet coating thickness in m
        """
        return flow_rate / (coating_speed * coating_width)

    def calculate_dry_thickness(self, wet_thickness, solid_content):
        """
        Calculate the drying rate based on wet thickness and solid content.

        The drying rate is proportional to the wet thickness and solid content,
        as these parameters affect the mass transfer during drying.

        Args:
            wet_thickness (float): Initial wet coating thickness in m
            solid_content (float): Fraction of solids in the coating (0-1)

        Returns:
            float: Drying rate in m/s
        """
        return wet_thickness * solid_content

    def calculate_defect_risk(self, coating_speed, gap_height, viscosity):
        """
        Assess the risk of coating defects based on process parameters.

        This method implements a simplified model to predict potential coating defects
        based on the relationship between shear rate and viscosity. Higher values of
        the ratio indicate increased risk of defects.

        Args:
            coating_speed (float): Speed of the coating process in m/s
            gap_height (float): Height of the coating gap in m
            K (float): Defect risk constant (10-100), higher values indicate more conservative risk assessment
            viscosity (float): Coating material viscosity in Pa·s

        Returns:
            bool: True if defect risk is high, False otherwise
        """
        K = 100  # Defect risk constant (10-100)
        return (coating_speed / gap_height) > (K * viscosity)

    def update_properties(
        self, machine_parameters: CoatingParameters, current_time_step: int = None
    ):
        """
        Update all computed properties dynamically.
        """
        self.wet_thickness = self.calculate_wet_thickness(
            machine_parameters.flow_rate,
            machine_parameters.coating_speed,
            machine_parameters.coating_width,
        )

        self.dry_thickness = self.calculate_dry_thickness(
            self.wet_thickness, self.solid_content
        )

        self.defect_risk = self.calculate_defect_risk(
            machine_parameters.coating_speed,
            machine_parameters.gap_height,
            self.viscosity,
        )

    def get_properties(self):
        return {
            # "temperature": round(self.temperature, 2), # not implemented!
            "solid_content": self.solid_content,
            "viscosity": round(self.viscosity, 4),
            "wet_thickness": round(self.wet_thickness, 4),
            "dry_thickness": round(self.dry_thickness, 4),
            # "shear_rate": round(self.shear_rate, 4), # process specific
            # "uniformity": round(self.uniformity, 4), # process specific
            "defect_risk": self.defect_risk,
        }
