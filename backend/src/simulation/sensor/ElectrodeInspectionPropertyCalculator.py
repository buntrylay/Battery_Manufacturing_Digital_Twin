class ElectrodeInspectionPropertyCalculator:
    """
    Evaluates electrode quality based on inspection criteria.
    Checks width, thickness, burr, and surface defect limits to determine pass/fail status.
    """

    def __init__(self, epsilon_width_max, epsilon_thickness_max, B_max, D_surface_max):
        """
        Initialize inspection thresholds.

        Parameters:
            epsilon_width_max (float): Maximum allowed width deviation
            epsilon_thickness_max (float): Maximum allowed thickness deviation
            B_max (float): Maximum allowed burr factor
            D_surface_max (float): Maximum allowed surface defect value
        """
        self.epsilon_width_max = epsilon_width_max
        self.epsilon_thickness_max = epsilon_thickness_max
        self.B_max = B_max
        self.D_surface_max = D_surface_max

    def is_pass(self, epsilon_width, delta_measured, delta_cal, B, D_detected):
        """
        Evaluate if electrode passes all inspection criteria.

        Parameters:
            epsilon_width (float): Width deviation
            delta_measured (float): Measured thickness
            delta_cal (float): Calculated (target) thickness
            B (float): Burr factor
            D_detected (float): Detected surface defect value

        Returns:
            dict: Pass/fail status for each criterion, calculated thickness deviation, and overall result
        """
        epsilon_thickness = delta_measured - delta_cal
        pass_width = abs(epsilon_width) <= self.epsilon_width_max
        pass_thickness = abs(epsilon_thickness) <= self.epsilon_thickness_max
        pass_burr = B <= self.B_max
        pass_surface = D_detected <= self.D_surface_max

        overall = "Pass" if all([pass_width, pass_thickness, pass_burr, pass_surface]) else "Fail"

        return {
            "Pass_width": pass_width,
            "Pass_thickness": pass_thickness,
            "Pass_burr": pass_burr,
            "Pass_surface": pass_surface,
            "epsilon_thickness": epsilon_thickness,
            "Overall": overall
        }