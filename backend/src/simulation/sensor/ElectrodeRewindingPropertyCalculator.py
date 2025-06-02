import numpy as np

class RewindingPropertyCalculator:
    def __init__(self, delta_cal, D_core, tau_initial, n_taper):
        self.delta_cal = delta_cal
        self.D_core = D_core
        self.tau_initial = tau_initial
        self.n_taper = n_taper

    def calculate_roll_diameter(self, L_wound):
        return np.sqrt(self.D_core**2 + (4 * L_wound * self.delta_cal) / np.pi)

    def calculate_taper_tension(self, D_roll):
        return self.tau_initial * (self.D_core / D_roll)**self.n_taper

    def calculate_roll_hardness(self, tau_rewind):
        return tau_rewind / self.delta_cal
