class CoatingPropertyCalculator:
    """
    Calculator class for coating properties and quality metrics in battery electrode manufacturing.
    
    This class implements physical models for calculating various coating properties including:
    - Shear rate and flow behavior
    - Wet coating thickness
    - Drying characteristics
    - Coating uniformity and defect risk assessment
    
    The calculations are based on fundamental coating process parameters and rheological properties.
    """
    
    def __init__(self):
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
        
    def calculate_shear_rate(self, coating_speed, gap_height):
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
        return coating_speed / gap_height
    
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
    
    def check_defect_risk(self, coating_speed, gap_height, shear_rate, viscosity):
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
        return (coating_speed / gap_height) > (self.K * viscosity)
    
    def calculate_uniformity(self, shear_rate):
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
