from simulation.battery_model.MixingModel import MixingModel

# def update_from_slurry(self, slurry):
#         """
#         Update coating machine properties from a slurry object.
#         Args:
#             slurry (Slurry): The slurry object from the mixing machine
#         """
#         with self.lock:
#             # Calculate total volume of solids
#             total_solids = slurry.AM + slurry.CA + slurry.PVDF
#             total_volume = total_solids + getattr(slurry, slurry.solvent)
#             self.solid_content = total_solids / total_volume if total_volume > 0 else 0
#             # Get viscosity from the slurry's calculator
#             self.viscosity_pa = slurry.viscosity
#             print(f"Updated {self.id} with properties from slurry")
#             print(f"Viscosity: {self.viscosity_pa:.2f} Pa·s, Solid Content: {self.solid_content:.2%}")

from simulation.battery_model.BaseModel import BaseModel

class CoatingModel(BaseModel):
    def __init__(self, slurry: MixingModel):
        total_solids = slurry.AM + slurry.CA + slurry.PVDF
        total_volume = total_solids + slurry.solvent
        self.solid_content = total_solids / total_volume if total_volume > 0 else 0
        self.viscosity = slurry.viscosity
        self.wet_thickness = 0
        self.dry_thickness = 0
        self.wet_width = 0
        self.uniformity_std = 0
        self.shear_rate = 0
        self.defect_risk = False
        """
        Initialise the coating property calculator with default parameters.
        
        Parameters:
            K (float): Defect risk constant (10-100), higher values indicate more conservative risk assessment
            base_std (float): Base standard deviation for uniformity calculations (0.01)
            nominal_shear_rate (float): Reference shear rate for normalization (500 1/s)
            sample_points (int): Number of points for sampling coating properties (800)
        """
        # Default parameters for calculations
        self.K = 100  # Defect risk constant (10-100)
        self.base_std = 0.01  # Base standard deviation
        self.nominal_shear_rate = 500  # 1/s
        self.sample_points = 800

    def update_shear_rate(self, coating_speed, gap_height):
        """
        Calculate the shear rate in the coating gap.
        
        The shear rate is a fundamental parameter that affects coating quality and uniformity.
        It is calculated as the ratio of coating speed to gap height.
        
        Args:
            coating_speed (float): Speed of the coating process in mm/s
            gap_height (float): Height of the coating gap in m
            
        Returns:
            float: Shear rate in 1/s
        """
        self.shear_rate = coating_speed / gap_height
    
    def update_wet_thickness(self, flow_rate, coating_speed, coating_width):
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
        self.wet_thickness = flow_rate / (coating_speed * coating_width)
    
    def update_dry_thickness(self):
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
        self.dry_thickness = self.wet_thickness * self.solid_content
    
    def update_defect_risk(self, coating_speed, gap_height, viscosity):
        """
        Assess the risk of coating defects based on process parameters.
        
        This method implements a simplified model to predict potential coating defects
        based on the relationship between shear rate and viscosity. Higher values of
        the ratio indicate increased risk of defects.
        
        Args:
            coating_speed (float): Speed of the coating process in m/s
            gap_height (float): Height of the coating gap in m
            shear_rate (float): Calculated shear rate in 1/s
            viscosity (float): Coating material viscosity in Pa·s
            
        Returns:
            bool: True if defect risk is high, False otherwise
        """
        self.defect_risk = (coating_speed / gap_height) > (self.K * self.viscosity)
    
    def update_uniformity_std(self, shear_rate):
        """
        Calculate coating uniformity based on shear rate.
        
        The uniformity is expressed as a standard deviation relative to the nominal
        shear rate. Lower values indicate better coating uniformity.
        
        Args:
            shear_rate (float): Calculated shear rate in 1/s
            
        Returns:
            float: Standard deviation of coating uniformity
        """
        return self.base_std * (shear_rate / self.nominal_shear_rate)
    
    def update_properties(self):
        """
        Update all computed properties.
        """
        self.shear_rate = self.calculate_shear_rate()
        
    def get_properties(self):
        return {
            "solid_content": self.solid_content,
            "viscosity": self.viscosity,
            "wet_thickness": self.wet_thickness,
            "wet_width": self.wet_width,
            "uniformity_wet": self.uniformity_std,
            "shear_rate": self.shear_rate,
        }