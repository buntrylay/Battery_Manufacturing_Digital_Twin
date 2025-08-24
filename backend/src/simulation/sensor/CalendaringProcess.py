import numpy as np

class CalendaringProcess:
    """
    Simulates the calendaring process in battery electrode manufacturing.
    Calendaring compresses the electrode to achieve desired thickness and porosity.
    """
    
    def __init__(self):
        # Material and process parameters
        self.E = 500e6       # Elastic modulus of electrode (Pa)
        self.k_p = 3.0       # Porosity reduction constant

    def _epsilon(self, delta_dry, h_roll):
        """
        Calculate compressive strain during calendaring.

        Parameters:
            dry_thickness (float): Initial dry electrode thickness (m)
            roll_gap (float): Gap between calendaring rolls (m)

        Returns:
            float: Compressive strain (unitless)
        """
        return (delta_dry - h_roll) / delta_dry

    def _sigma_calc(self, epsilon_val):
        """
        Calculate applied stress based on compressive strain.

        Parameters:
            strain (float): Compressive strain (unitless)

        Returns:
            float: Applied stress (Pa)
        """
        return self.E * epsilon_val

    def _porosity_reduction(self, epsilon_val, phi_initial):
        """
        Calculate reduced porosity after calendaring.

        Parameters:
            strain (float): Compressive strain (unitless)
            initial_porosity (float): Initial porosity (fraction, 0-1)

        Returns:
            float: Reduced porosity (fraction, 0-1)
        """
        return phi_initial * np.exp(-self.k_p * epsilon_val)

    def _defect_risk(self, applied_sigma, theoretical_sigma, time_step):
        """
        Assess risk of defects (e.g., cracks) due to excessive pressure.

        Parameters:
            applied_stress (float): Actual applied stress (Pa)
            safe_stress (float): Theoretical safe stress (Pa)
            time_step (float): Current simulation time (s)

        Returns:
            tuple: (bool, str) - True and warning message if risk detected, else False and empty string
        """
        if applied_sigma > 2 * theoretical_sigma:
            return True, f"Warning: Excessive pressure at t = {time_step}s may cause cracks."
        return False, ""