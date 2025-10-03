from simulation.battery_model.BaseModel import BaseModel
from simulation.battery_model.RewindingModel import RewindingModel
import numpy as np

class ElectrolyteFillingModel(BaseModel):
    def __init__(self, rewinding_model: RewindingModel):
        # from rewinding
        self.final_thickness = rewinding_model.delta_sl
        self.porosity = rewinding_model.porosity
        self.final_width = rewinding_model.final_width
        self.epsilon_width = rewinding_model.epsilon_width
        self.length = rewinding_model.L_wound

        # state
        self.V_sep = 0
        self.V_elec = 0
        self.V_max = 0
        self.eta_wetting = 0
        self.V_elec_filling = 0
        self.defect_risk = False

        # constant
        self.rho_elec = 1.2 

    def V_sep_calc(self):
        return 0.05 * self.length

    def V_elec_calc(self):
        return self.length * self.final_width * self.final_thickness

    def V_max_calc(self):
        return (self.porosity * (self.V_elec + self.V_sep))

    def eta_wetting_calc(self, t, soaking_time):
        return 1 - np.exp(-3 * (t / soaking_time))

    def update_properties(self, params):
        t = getattr(self, "current_time_step", 0)
        self.V_sep = self.V_sep_calc()
        self.V_elec = self.V_elec_calc()
        self.V_max = self.V_max_calc()
        self.eta_wetting = self.eta_wetting_calc(t, params.Soaking_time)
        self.V_elec_filling = self.eta_wetting * self.V_max
        self.defect_risk = self.V_elec_filling < 0.8 * self.V_max

    def get_properties(self):
        return {
            "final_thickness": float(self.final_thickness),
            "porosity": float(self.porosity),
            "final_width": float(self.final_width),
            "epsilon_width": float(self.epsilon_width),
            "wound_length": float(self.length),
            "V_sep": float(self.V_sep),
            "V_elec": float(self.V_elec),
            "V_max": float(self.V_max),
            "eta_wetting": float(self.eta_wetting),
            "V_elec_filling": float(self.V_elec_filling),
            "defect_risk": bool(self.defect_risk)
        }
