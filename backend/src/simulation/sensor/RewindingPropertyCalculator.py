import numpy as np
class RewindingPropertyCalculator:
    """
    Calculates rewinding-related properties for battery electrode manufacturing.
    Used to estimate roll diameter, tension profile, and roll hardness during rewinding.
    """

    def __init__(self):
        # Core diameter of the roll (m)
        self.D_core = 0.2
        
    def D_roll(self, L_wound, delta_cal):
        """
        Calculate the diameter of the roll after winding a given length.

        Parameters:
            L_wound (float): Length of electrode wound onto the roll (m)
            delta_cal (float): Electrode thickness (m)

        Returns:
            float: Roll diameter (m)
        """
        return np.sqrt(self.D_core**2 + (4 * L_wound * delta_cal)/np.pi)

    def tau_rewind(self, D_roll, tau_initial, n_taper):
        """
        Calculate the rewinding tension as the roll diameter increases.

        Parameters:
            D_roll (float): Current roll diameter (m)
            tau_initial (float): Initial tension (N)
            n_taper (float): Tension taper exponent (unitless)

        Returns:
            float: Tapered tension (N)
        """
        return tau_initial * (self.D_core /D_roll)**n_taper

    def H_roll(self, delta_cal, tau_rewind):
        """
        Calculate roll hardness based on rewinding tension and electrode thickness.

        Parameters:
            delta_cal (float): Electrode thickness (m)
            tau_rewind (float): Rewinding tension (N)

        Returns:
            float: Roll hardness (arbitrary units)
        """
        return tau_rewind / delta_cal