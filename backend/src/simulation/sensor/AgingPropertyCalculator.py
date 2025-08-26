import numpy as np
class AgingPropertyCalculator:
    """
    Calculates aging-related properties for battery cells.
    Includes state-of-charge decay, open-circuit voltage drift, and leakage current estimation.
    """

    def __init__(self, Q_cell = 2.0, V_min = 3.0, V_max = 4.2):
        """
        Initialize cell parameters.

        Parameters:
            Q_cell (float): Cell capacity (Ah)
            V_min (float): Minimum cell voltage (V)
            V_max (float): Maximum cell voltage (V)
        """
        self.Q_cell = Q_cell
        self.V_min = V_min
        self.V_max = V_max

    def soc_delay(self, SOC_0, k_leak, t):
        """
        Calculate state-of-charge (SOC) decay over time due to leakage.

        Parameters:
            SOC_0 (float): Initial state-of-charge (fraction, 0-1)
            k_leak (float): Leakage rate constant (1/time)
            t (float): Time (same units as k_leak)

        Returns:
            float: SOC after time t
        """
        return SOC_0 * np.exp(-k_leak * t)
    
    def ocv_drift(self, SOC):
        """
        Calculate open-circuit voltage (OCV) as a function of SOC.

        Parameters:
            SOC (float): State-of-charge (fraction, 0-1)

        Returns:
            float: Open-circuit voltage (V)
        """
        return self.V_min + (self.V_max - self.V_min) * SOC
    
    def leakage_current(self, k_leak):
        """
        Calculate leakage current based on leakage rate and cell capacity.

        Parameters:
            k_leak (float): Leakage rate constant (1/s)

        Returns:
            float: Leakage current (A)
        """
        return k_leak * self.Q_cell * 3600