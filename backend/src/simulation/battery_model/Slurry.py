class Slurry:
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
        Initialize a new Slurry instance.
        
        Args:
            electrode_type (str): The type of electrode ("Anode" or "Cathode")
        """
        self.AM = 0  # Active Material
        self.CA = 0  # Conductive Additive
        self.PVDF = 0  # PVDF Binder
        if electrode_type == "Anode":
            self.electrode_type = "Anode"
            self.H2O = 0  # Solvent for anode
            self.solvent = "H2O"
        elif electrode_type == "Cathode":
            self.electrode_type = "Cathode"
            self.NMP = 0  # Solvent for cathode
            self.solvent = "NMP"
        
        self.viscosity = 0
        self.density = 0
        self.yield_stress = 0

    def add(self, component, amount):
        """
        Add a specified amount of a component to the slurry.
        
        Args:
            component (str): The component to add ('AM', 'CA', 'PVDF', or 'H2O' or 'NMP')
            amount (float): The amount of the component to add
        """
        setattr(self, component, getattr(self, component) + amount)

    def get_total_volume(self):
        """
        Calculate the current total volume of all components in the slurry.
        
        Returns:
            float: The sum of all components (AM + CA + PVDF + H2O or NMP)
        """
        return self.AM + self.CA + self.PVDF + (self.H2O if self.electrode_type == "Anode" else self.NMP)
    
    def update_properties(self, viscosity, density, yield_stress):
        """
        Update the properties of the slurry.
        
        Args:
            viscosity (float): The viscosity of the slurry
            density (float): The density of the slurry
            yield_stress (float): The yield stress of the slurry
        """
        self.viscosity = viscosity
        self.density = density
        self.yield_stress = yield_stress
