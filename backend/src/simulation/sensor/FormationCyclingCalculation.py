import numpy as np

class FormationCyclingCalculation:
    def calculate_sei_efficiency(self, k_sei, t, t50):
        return 1 / (1 + np.exp(-k_sei * (t - t50)))

    def calculate_cell_capacity_ah(self, Q_theoretical_A, calculate_sei_efficiency):
        return Q_theoretical_A * calculate_sei_efficiency
    
    def calculate_voltage_charge_cc(self, t, V0_cell_V, I_charge_A, cell_capacity_A):
        return V0_cell_V + (I_charge_A * t)/cell_capacity_A