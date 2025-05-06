from Slurry import Slurry

class SlurryPropertyCalculator:

    def __init__(self, slurry: Slurry, RHO_values: dict, WEIGHTS_values: dict):
        self.slurry = slurry
        self.RHO = RHO_values
        self.WEIGHTS = WEIGHTS_values
    
    def calculate_density(self):
        m = lambda x: getattr(self.slurry, x) * self.RHO[x]
        total_mass = sum(m(c) for c in self.RHO)
        volume = self.slurry.get_total_volume()
        return total_mass / volume if volume else 0
    
    def calculate_viscosity(self, max_solid_fraction=0.63, intrinsic_viscosity=3):
        total_volume = self.slurry.get_total_volume()
        solid_volume = self.slurry.AM + self.slurry.CB + self.slurry.PVDF
        phi = solid_volume / total_volume if total_volume else 0
        if phi >= max_solid_fraction:
            phi = max_solid_fraction - 0.001
        return (1 - (phi / max_solid_fraction)) ** (-intrinsic_viscosity * max_solid_fraction) * 2
    
    def calculate_yield_stress(self):
        m = lambda x: getattr(self.slurry, x) * self.RHO[x]
        return (self.WEIGHTS['a'] * m("AM") +
                self.WEIGHTS['b'] * m("PVDF") +
                self.WEIGHTS['c'] * m("CA") +
                self.WEIGHTS['s'] * m("SV"))