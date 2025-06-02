import numpy as np
class ElectrolyteFillingCalculation:
    
    def __init__(self):
        self.T_sep = 0.002 #cm
        self.A_sep = 100 # cm2
        self.k_wet = 0.00045 
        #Assumption 30% EC, 30% DMC, 30% EMC, and 10% LiPF₆ Meeting Week 13
        self.elec_density = 1174 #kg/m3
        
    def V_sep(self):
        return self.T_sep * self.A_sep  #Volume for Separator Find in Technical Meeting 13
    
    def V_elec(self, length, width, thickness):
        return length * width * thickness * 1e6
    
    def phi_elec(self):
        return self.elec_density #Meeting Week 13
    
    def V_max(self, phi_final, V_elec, V_sep):
        return (phi_final * V_elec) + V_sep
    
    def eta_wetting(self, t):
        return 1 - np.exp(-self.k_wet * t)
    
    def V_elec_filling(self, eta_wetting, V_max):
        return eta_wetting * V_max
    
    def defect_risk(self, V_elec_filling, V_max):
        if V_elec_filling < 0.95 * V_max:
            return "Underfill"
        elif V_elec_filling > 1.05 * V_max:
            return "Overfill"
        else: 
            return "Pass"
        
        
        