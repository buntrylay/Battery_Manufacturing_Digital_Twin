import numpy as np

class SlittingPropertyCalculator:
    def __init__(self):
        self.C = 1.0
        self.v_ref = 1.0
        self.tau_ref = 100
        self.max_width_deviation = 0.1
        self.max_burr_threshold = 2.0
        

    def simulate_width_variation(self, target_width):
        return target_width + np.random.normal(0, 0.05)

    def calculate_cut_accuracy(self, w_final, w_target):
        return w_final - w_target

    def calculate_burr_factor(self, S, v_slit, tau_slit):
        return (self.C / S) * (v_slit / self.v_ref) * (tau_slit / self.tau_ref)

    def is_defective(self, epsilon_width, burr_factor):
        return abs(epsilon_width) > self.max_width_deviation or burr_factor > self.max_burr_threshold
