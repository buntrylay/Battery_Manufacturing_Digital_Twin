class ElectrodeInspectionPropertyCalculator:
    def __init__(self, epsilon_width_max, epsilon_thickness_max, B_max, D_surface_max):
        self.epsilon_width_max = epsilon_width_max
        self.epsilon_thickness_max = epsilon_thickness_max
        self.B_max = B_max
        self.D_surface_max = D_surface_max

    def is_pass(self, epsilon_width, delta_measured, delta_cal, B, D_detected):
        epsilon_thickness = delta_measured - delta_cal
        return {
            "Pass_width": abs(epsilon_width) <= self.epsilon_width_max,
            "Pass_thickness": abs(epsilon_thickness) <= self.epsilon_thickness_max,
            "Pass_burr": B <= self.B_max,
            "Pass_surface": D_detected <= self.D_surface_max,
            "epsilon_thickness": epsilon_thickness,
            "Overall": "Pass" if all([
                abs(epsilon_width) <= self.epsilon_width_max,
                abs(epsilon_thickness) <= self.epsilon_thickness_max,
                B <= self.B_max,
                D_detected <= self.D_surface_max
            ]) else "Fail"
        }