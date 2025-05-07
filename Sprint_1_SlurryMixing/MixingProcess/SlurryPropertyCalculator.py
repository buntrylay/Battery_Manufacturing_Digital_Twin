from Slurry import Slurry

class SlurryPropertyCalculator:
    """
    A calculator class for determining various physical properties of battery slurry.
    
    This class calculates important slurry properties such as density, viscosity, and yield stress
    based on the composition and physical properties of the slurry components.
    
    Attributes:
        RHO (dict): Dictionary of density values for each component (g/cm³)
        WEIGHTS (dict): Dictionary of weight coefficients for yield stress calculation
    """

    def __init__(self, RHO_values: dict, WEIGHTS_values: dict):
        """
        Initialise a new SlurryPropertyCalculator instance.
        
        Args:
            RHO_values (dict): Dictionary of density values for each component
            WEIGHTS_values (dict): Dictionary of weight coefficients for calculations
        """
        self.RHO = RHO_values
        self.WEIGHTS = WEIGHTS_values
    
    def calculate_density(self, slurry: Slurry):
        """
        Calculate the density of the slurry.
        
        The density is calculated as the total mass divided by total volume,
        where mass is the product of component volume and its density.
        
        Returns:
            float: The calculated density in g/cm³, or 0 if total volume is 0
        """
        # Lambda function to calculate mass of a component (volume * density)
        m = lambda x: getattr(slurry, x) * self.RHO[x]
        total_mass = sum(m(c) for c in self.RHO)
        volume = slurry.get_total_volume()
        return total_mass / volume if volume else 0
    
    def calculate_viscosity(self, slurry: Slurry, max_solid_fraction=0.63, intrinsic_viscosity=3):
        """
        Calculate the viscosity of the slurry using the Krieger-Dougherty model.
        
        The viscosity is calculated based on the solid fraction (phi) and follows
        the Krieger-Dougherty equation: η = (1 - φ/φm)^(-[η]φm)
        
        Args:
            slurry (Slurry): The slurry object containing component amounts
            max_solid_fraction (float): Maximum packing fraction (default: 0.63)
            intrinsic_viscosity (float): Intrinsic viscosity parameter (default: 3)
            
        Returns:
            float: The calculated viscosity in Pa·s
        """
        total_volume = slurry.get_total_volume()

        # Calculate solid volume (sum of AM, CA, and PVDF)
        solid_volume = slurry.AM + slurry.CA + slurry.PVDF

        # Calculate solid fraction
        phi = solid_volume / total_volume if total_volume else 0

        # Cap solid fraction to prevent infinite viscosity
        if phi >= max_solid_fraction:
            phi = max_solid_fraction - 0.001

        # Apply Krieger-Dougherty equation with scaling factor of 2
        return (1 - (phi / max_solid_fraction)) ** (-intrinsic_viscosity * max_solid_fraction) * 2
    
    def calculate_yield_stress(self, slurry: Slurry):
        """
        Calculate the yield stress of the slurry.
        
        The yield stress is calculated as a weighted sum of the masses of different
        components, where each component's contribution is weighted by its respective
        coefficient from the WEIGHTS dictionary.
        
        Returns:
            float: The calculated yield stress in Pa
        """
        # Lambda function to calculate mass of a component (volume * density)
        m = lambda x: getattr(slurry, x) * self.RHO[x]

        # Calculate weighted sum of component masses
        return (self.WEIGHTS['a'] * m("AM") +  # Active Material contribution
                self.WEIGHTS['b'] * m("PVDF") + # PVDF Binder contribution
                self.WEIGHTS['c'] * m("CA") +   # Conductive Additive contribution
                self.WEIGHTS['s'] * (m("H2O") if slurry.electrode_type == "Anode" else m("NMP")))    # Solvent contribution