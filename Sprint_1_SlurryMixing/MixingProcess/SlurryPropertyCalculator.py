from Slurry import Slurry

class SlurryPropertyCalculator:
    RHO = {"AM": 2.26, "CB": 1.8, "PVDF": 1.78, "NMP": 1.0}
    WEIGHTS = {"a": 0.9, "b": 2.5, "c": 0.3, "s": -0.5}

    def __init__(self, slurry: Slurry):
        self.slurry = slurry
    
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
                self.WEIGHTS['c'] * m("CB") +
                self.WEIGHTS['s'] * m("NMP"))