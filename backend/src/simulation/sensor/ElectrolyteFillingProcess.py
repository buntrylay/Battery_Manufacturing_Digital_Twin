import numpy as np
class ElectrolyteFillingCalculation:
    """
    Calculates properties and outcomes for the electrolyte filling process in battery manufacturing.
    Includes separator and electrode volume, electrolyte density, wetting kinetics, and defect risk assessment.
    """
    
    def __init__(self):
        # Separator thickness (cm)
        self.T_sep = 0.002

        # Separator area (cm^2)
        self.A_sep = 100

        # Wetting rate constant (empirical)
        self.k_wet = 0.00045

        # Electrolyte density (kg/m^3), based on assumed composition
        self.elec_density = 1174
        
    def V_sep(self):
        """
        Calculate separator volume.

        Returns:
            float: Separator volume (cm^3)
        """
        return self.T_sep * self.A_sep  #Volume for Separator Find in Technical Meeting 13
    
    def V_elec(self, length, width, thickness):
        """
        Calculate electrode volume.

        Parameters:
            length (float): Electrode length (m)
            width (float): Electrode width (m)
            thickness (float): Electrode thickness (m)

        Returns:
            float: Electrode volume (cm^3)
        """
        return length * width * thickness * 1e6
    
    def phi_elec(self):
        """
        Return electrolyte density.

        Returns:
            float: Electrolyte density (kg/m^3)
        """
        return self.elec_density #Meeting Week 13
    
    def V_max(self, phi_final, V_elec, V_sep):
        """
        Calculate maximum fillable volume.

        Parameters:
            phi_final (float): Final porosity (fraction)
            V_elec (float): Electrode volume (cm^3)
            V_sep (float): Separator volume (cm^3)

        Returns:
            float: Maximum electrolyte volume (cm^3)
        """
        return (phi_final * V_elec) + V_sep
    
    def eta_wetting(self, t):
        """
        Calculate wetting efficiency as a function of time.

        Parameters:
            t (float): Time (arbitrary units, typically seconds)

        Returns:
            float: Wetting efficiency (fraction, 0-1)
        """
        return 1 - np.exp(-self.k_wet * t)
    
    def V_elec_filling(self, eta_wetting, V_max):
        """
        Calculate actual filled electrolyte volume.

        Parameters:
            eta_wetting (float): Wetting efficiency (fraction)
            V_max (float): Maximum fillable volume (cm^3)

        Returns:
            float: Actual filled volume (cm^3)
        """
        return eta_wetting * V_max
    
    def defect_risk(self, V_elec_filling, V_max):
        """
        Assess risk of underfill or overfill defects.

        Parameters:
            V_elec_filling (float): Actual filled volume (cm^3)
            V_max (float): Maximum fillable volume (cm^3)

        Returns:
            str: "Underfill", "Overfill", or "Pass"
        """
        if V_elec_filling < 0.95 * V_max:
            return "Underfill"
        elif V_elec_filling > 1.05 * V_max:
            return "Overfill"
        else: 
            return "Pass"
        
        
        