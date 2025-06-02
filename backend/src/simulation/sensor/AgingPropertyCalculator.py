import numpy as np
class AgingPropertyCalculator:
    def __init__(self, Q_cell = 2.0, V_min = 3.0, V_max = 4.2):
        self.Q_cell = Q_cell
        self.V_min = V_min
        self.V_max = V_max

    def soc_delay(self, SOC_0, k_leak, t):
        return SOC_0 * np.exp(-k_leak * t)
    
    def ocv_drift(self, SOC):
        return self.V_min + (self.V_max - self.V_min) * SOC
    
    def leakage_current(self, k_leak):
        return k_leak * self.Q_cell * 3600