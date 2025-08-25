import numpy as np

class SlittingPropertyCalculator:
    """
    Calculates slitting-related properties for battery electrode manufacturing.
    Used to simulate width variation, cut accuracy, burr formation, and defect detection.
    
    Burr factor - quantifies the amount or severity of burrs—small, unwanted projections or rough edges—created along the cut edges of the electrode material when it is slit to size. 
    High burr factors indicate rougher, less precise cuts, which can lead to defects, safety issues, or poor performance in the final battery.
    """

    def __init__(self):
        # Model parameters for slitting process
        self.C = 1.0                    # Burr formation constant (empirical)
        self.v_ref = 1.0                # Reference slitting speed (m/s)
        self.tau_ref = 100              # Reference blade sharpness (arbitrary units)
        self.max_width_deviation = 0.1  # Maximum allowed width deviation (mm or m, as per context)
        self.max_burr_threshold = 2.0   # Maximum allowed burr factor (arbitrary units)

    def simulate_width_variation(self, target_width):
        """
        Simulate actual slit width with random variation.

        Parameters:
            target_width (float): Target width after slitting

        Returns:
            float: Simulated final width
        """
        return target_width + np.random.normal(0, 0.05)

    def calculate_cut_accuracy(self, w_final, w_target):
        """
        Calculate deviation between final and target width.

        Parameters:
            w_final (float): Final measured width
            w_target (float): Target width

        Returns:
            float: Width deviation
        """
        return w_final - w_target

    def calculate_burr_factor(self, S, v_slit, tau_slit):
        """
        Calculate burr factor based on slitting parameters.

        Parameters:
            S (float): Material strength or thickness (arbitrary units)
            v_slit (float): Slitting speed (m/s)
            tau_slit (float): Blade sharpness (arbitrary units)

        Returns:
            float: Burr factor (higher means more burr)
        """
        return (self.C / S) * (v_slit / self.v_ref) * (tau_slit / self.tau_ref)

    def is_defective(self, epsilon_width, burr_factor):
        """
        Determine if the slit electrode is defective based on width deviation and burr.

        Parameters:
            epsilon_width (float): Width deviation
            burr_factor (float): Burr factor

        Returns:
            bool: True if defective, False otherwise
        """
        return abs(epsilon_width) > self.max_width_deviation or burr_factor > self.max_burr_threshold
