import numpy as np

class FormationCyclingCalculation:
    """
    Calculates properties related to the formation cycling process in battery manufacturing.
    Includes SEI (Solid Electrolyte Interphase) formation efficiency, cell capacity, and voltage during charging.
    """

    def calculate_sei_efficiency(self, k_sei, t, t50):
        """
        Calculate SEI formation efficiency as a function of time.

        Parameters:
            k_sei (float): SEI formation rate constant
            t (float): Time (arbitrary units, typically hours or cycles)
            t50 (float): Time at which efficiency is 50%

        Returns:
            float: SEI formation efficiency (fraction, 0-1)
        """
        return 1 / (1 + np.exp(-k_sei * (t - t50)))

    def calculate_cell_capacity_ah(self, Q_theoretical_A, calculate_sei_efficiency):
        """
        Calculate actual cell capacity after SEI formation.

        Parameters:
            Q_theoretical_A (float): Theoretical cell capacity (Ah)
            calculate_sei_efficiency (float): SEI formation efficiency (fraction, 0-1)

        Returns:
            float: Actual cell capacity (Ah)
        """
        return Q_theoretical_A * calculate_sei_efficiency
    
    def calculate_voltage_charge_cc(self, t, V0_cell_V, I_charge_A, cell_capacity_A):
        """
        Calculate cell voltage during constant current (CC) charging.

        Parameters:
            t (float): Charging time (h or s)
            V0_cell_V (float): Initial cell voltage (V)
            I_charge_A (float): Charging current (A)
            cell_capacity_A (float): Cell capacity (Ah)

        Returns:
            float: Cell voltage (V)
        """
        return V0_cell_V + (I_charge_A * t)/cell_capacity_A