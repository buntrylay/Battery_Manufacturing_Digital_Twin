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