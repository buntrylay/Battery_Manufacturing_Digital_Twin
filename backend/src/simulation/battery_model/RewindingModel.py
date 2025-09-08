from simulation.battery_model.BaseModel import BaseModel
from simulation.battery_model.ElectrodeInspectionModel import ElectrodeInspectionModel
import numpy as np

class RewindingModel(BaseModel):
    def __init__(self, 
        inspection_model : ElectrodeInspectionModel):        
        # from inspection
        self.delta_sl = inspection_model.final_thickness
        self.porosity = inspection_model.porosity
        self.final_width = inspection_model.final_width
        self.epsilon_width = inspection_model.epsilon_width

        # state
        self.L_wound = 0
        self.D_roll = 0
        self.H_roll = 0
        self.tau_rewind = 0
        self.D_core = 0.2

    def D_roll_calc(self, L_wound, delta_sl, D_core):
        return np.sqrt(D_core**2 + (4 * L_wound * delta_sl) / np.pi)

    def tau_rewind_calc(self, D_roll, tau_initial, n_taper, D_core):
        return tau_initial * (D_core / D_roll) ** n_taper

    def H_roll_calc(self, delta_sl, tau_rewind):
        return tau_rewind / delta_sl

    def update_properties(self, params, interval=1):
        self.L_wound += params.rewinding_speed * interval
        self.D_roll = self.D_roll_calc(self.L_wound, self.delta_sl, self.D_core)
        self.tau_rewind = self.tau_rewind_calc(self.D_roll, params.initial_tension, params.tapering_steps, self.D_core)
        self.H_roll = self.H_roll_calc(self.delta_sl, self.tau_rewind)

    def get_properties(self):
        return {
            "final_thickness": float(self.delta_sl),
            "porosity": float(self.porosity),
            "final_width": float(self.final_width),
            "epsilon_width": float(self.epsilon_width),
            "wound_length": float(self.L_wound),
            "roll_diameter": float(self.D_roll),
            "web_tension": float(self.tau_rewind),
            "roll_hardness": float(self.H_roll)
        }