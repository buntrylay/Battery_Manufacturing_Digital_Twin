class Slurry:
    """
    A class representing a battery slurry mixture containing active material (AM), 
    conductive additive (CA), PVDF binder, and solvent (SV).
    
    Attributes:
        total_volume (float): The target total volume of the slurry
        AM (float): Amount of active material in the slurry
        CA (float): Amount of conductive additive in the slurry
        PVDF (float): Amount of PVDF binder in the slurry
        SV (float): Amount of solvent in the slurry
    """
    
    def __init__(self, volume):
        """
        Initialize a new Slurry instance.
        
        Args:
            volume (float): The target total volume of the slurry
        """
        self.total_volume = volume
        self.AM = 0  # Active Material
        self.CA = 0  # Conductive Additive
        self.PVDF = 0  # PVDF Binder
        self.SV = 0  # Solvent

    def add(self, component, amount):
        """
        Add a specified amount of a component to the slurry.
        
        Args:
            component (str): The component to add ('AM', 'CA', 'PVDF', or 'SV')
            amount (float): The amount of the component to add
        """
        setattr(self, component, getattr(self, component) + amount)

    def get_total_volume(self):
        """
        Calculate the current total volume of all components in the slurry.
        
        Returns:
            float: The sum of all components (AM + CA + PVDF + SV)
        """
        return self.AM + self.CA + self.PVDF + self.SV