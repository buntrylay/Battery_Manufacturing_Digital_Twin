from simulation.battery_model.BaseModel import BaseModel
from simulation.battery_model.SlittingModel import SlittingModel
import numpy as np

class ElectrodeInspectionModel(BaseModel):
    def __init__(self,
        slitting_model: SlittingModel):
        # from slitting
        self.final_width = slitting_model.width_final
        self.final_thickness = slitting_model.final_thickness
        self.epsilon_width = slitting_model.epsilon_width
        self.burr_factor = slitting_model.burr_factor
        self.porosity = slitting_model.porosity
        # state
        self.epsilon_thickness = 0
        self.D_detected = 0
        self.pass_width = False
        self.pass_thickness = False
        self.pass_burr = False
        self.pass_surface = False
        self.overall = False

    def update_properties(self, params):
        self.epsilon_thickness = (self.final_thickness * 1e-6) * np.random.uniform(-1, 1)
        self.D_detected = np.random.randint(0, 3)
        self.pass_width = abs(self.epsilon_width) <= params.epsilon_width_max       
        self.pass_thickness = abs(self.epsilon_thickness) <= params.epsilon_thickness_max
        self.pass_burr = self.burr_factor <= params.B_max
        self.pass_surface = self.D_detected <= params.D_surface_max
        self.overall = all([self.pass_width, self.pass_thickness, self.pass_burr, self.pass_surface])


    def get_properties(self):
        return {
            "final_width": self.final_width,
            "final_thickness": self.final_thickness,
            "epsilon_width": self.epsilon_width,
            "burr_factor": self.burr_factor,
            "epsilon_thickness": self.epsilon_thickness,
            "D_detected": self.D_detected,
            "Pass_width": self.pass_width,
            "Pass_thickness": self.pass_thickness,
            "Pass_burr": self.pass_burr,
            "Pass_surface": self.pass_surface,
            "Overall": self.overall,
        }