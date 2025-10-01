import numpy as np

class CalendaringProcess:
    def __init__(self):
        ###Controlled Variables
        self.E = 500e6                 # Elastic modulus (Pa)
        self.k_p = 3.0                 # Porosity reduction constant

    def _epsilon(self, delta_dry, h_roll):
        return (delta_dry - h_roll) / delta_dry

    def _sigma_calc(self, epsilon_val):
        return self.E * epsilon_val

    def _porosity_reduction(self, epsilon_val, phi_initial):
        return phi_initial * np.exp(-self.k_p * epsilon_val)

    def _defect_risk(self, applied_sigma, theoretical_sigma, time_step):
        if applied_sigma > 2 * theoretical_sigma:
            return True, f"Warning: Excessive pressure at t = {time_step}s may cause cracks."
        return False, ""