import numpy as np
class RewindingPropertyCalculator:
    """
    A class to calculate rewinding properties for a simulation.
    """

    def __init__(self):
        self.D_core = 0.2
        
    def L_wound(self, v_rewind, delta_cal):
        return v_rewind * delta_cal

    def D_roll(self, L_wound, delta_cal):
        return np.sqrt(self.D_core**2 +2 * (4+ L_wound * delta_cal)/np.pi)

    def tau_rewind(self, D_roll, tau_initial, n_taper):
        return tau_initial * (self.D_core /D_roll)**n_taper

    def H_roll(self, delta_cal, tau_rewind):
        return tau_rewind / delta_cal