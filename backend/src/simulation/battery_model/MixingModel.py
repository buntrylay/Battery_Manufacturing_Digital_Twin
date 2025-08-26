from dataclasses import dataclass
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
        self.AM = 0  # Active Material
        self.CA = 0  # Conductive Additive
        self.PVDF = 0  # PVDF Binder
        self.electrode_type = electrode_type
        if electrode_type == "Anode":
            self.H2O = 0  # Solvent for anode
            self.solvent = "H2O"
        elif self.electrode_type == "Cathode":
            self.NMP = 0  # Solvent for cathode
            self.solvent = "NMP"
        # computed properties
        self.viscosity = 0
        self.density = 0
        self.yield_stress = 0
        # Add density and weight coefficients as class constants
        self.RHO = {"AM": 2.26, "CA": 1.8, "PVDF": 1.17, "H2O": 1.0, "NMP": 1.03}
        self.WEIGHTS = {"a": 0.85, "b": 2.2, "c": 0.3, "s": -0.4}
        # Override for cathode
        if electrode_type == "Cathode":
            self.RHO.update({"AM": 2.11, "PVDF": 1.78})
            self.WEIGHTS.update({"a": 0.9, "b": 2.5, "s": -0.5})


    def add(self, component, amount):
        """
        Add a specified amount of a component to the slurry.
        
        Args:
            component (str): The component to add ('AM', 'CA', 'PVDF', or 'H2O' or 'NMP')
            amount (float): The amount of the component to add
        """
        setattr(self, component, getattr(self, component) + amount)

    def calculate_density(self):
        """Calculate density using component volumes and densities"""
        total_mass = sum(getattr(self, c) * self.RHO[c] for c in self.RHO if hasattr(self, c))
        volume = self.get_total_volume()
        return total_mass / volume if volume > 0 else 0

    def calculate_viscosity(self, max_solid_fraction=0.63, intrinsic_viscosity=3):
        """Calculate viscosity using Krieger-Dougherty model"""
        total_volume = self.get_total_volume()
        solid_volume = self.AM + self.CA + self.PVDF
        phi = solid_volume / total_volume if total_volume > 0 else 0
        
        if phi >= max_solid_fraction:
            phi = max_solid_fraction - 0.001
            
        return (1 - (phi / max_solid_fraction)) ** (-intrinsic_viscosity * max_solid_fraction) * 0.017

    def calculate_yield_stress(self):
        """Calculate yield stress using weighted component masses"""
        m = lambda x: getattr(self, x) * self.RHO[x]
        solvent_key = "H2O" if self.electrode_type == "Anode" else "NMP"
        
        return (self.WEIGHTS['a'] * m("AM") + 
                self.WEIGHTS['b'] * m("PVDF") + 
                self.WEIGHTS['c'] * m("CA") + 
                self.WEIGHTS['s'] * m(solvent_key))
    
    def update_properties(self):
        """Update all computed properties"""
        self.density = self.calculate_density()
        self.viscosity = self.calculate_viscosity()
        self.yield_stress = self.calculate_yield_stress()

    def get_total_volume(self):
        """
        Calculate the current total volume of all components in the slurry.
        
        Returns:
            float: The sum of all components (AM + CA + PVDF + H2O or NMP)
        """
        return self.AM + self.CA + self.PVDF + (self.H2O if self.electrode_type == "Anode" else self.NMP)

    def get_properties(self):
        return {
            "AM_volume": self.AM,
            "CA_volume": self.CA,
            "PVDF_volume": self.PVDF,
            f"{self.solvent}_volume": getattr(self, self.solvent),
            "viscosity": self.viscosity,
            "density": self.density,
            "yield_stress": self.yield_stress,
            "total_volume": self.get_total_volume(),
        }