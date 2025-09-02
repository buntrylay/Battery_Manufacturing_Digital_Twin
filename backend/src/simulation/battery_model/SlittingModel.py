from simulation.battery_model.BaseModel import BaseModel
from simulation.battery_model.CalendaringModel import CalendaringModel
import numpy as np
class SlittingModel(BaseModel):
    def __init__(self, calendaring_model: CalendaringModel):
        # from calendaring
        self.dry_thickness = calendaring_model.dry_thickness
        self.porosity = calendaring_model.porosity
        self.final_thickness = calendaring_model.final_thickness    
       
        # state
        self.width_final = 0
        self.epsilon_width = 0
        self.burr_factor = 0
        self.defect_risk = False

        # material constant
        self.C = 1.0
        self.v_ref = 1.0
        self.tau_ref = 100
        self.max_width_deviation = 0.1
        self.max_burr_threshold = 2.0

    def simulate_width_variation(self, target_width):
        return target_width + np.random.normal(0, 0.05)

    def calculate_epsilon_width(self, w_final, w_target):
        return w_final - w_target

    def calculate_burr_factor(self, S, v_slit, tau_slit):
        return (self.C / S) * (v_slit / self.v_ref) * (tau_slit / self.tau_ref)

    def defect_check(self, epsilon_width, burr_factor):
        return abs(epsilon_width) > self.max_width_deviation or burr_factor > self.max_burr_threshold

    def update_properties(self, simulate_width_variation, calculate_burr_factor, defect_check):
        self.width_final = self.simulate_width_variation(self.target_width)
        self.epsilon_width = self.calculate_epsilon_width(self.width_final, self.target_width)
        self.burr_factor = self.calculate_burr_factor(self.blade_sharpness, self.slitting_speed, self.slitting_tension)
        self.defect_risk = self.defect_check(self.epsilon_width, self.burr_factor)
        self.final_thickness = self.dry_thickness  # assuming no thickness change during slitting

    def get_properties(self):
        return {
            "final_thickness": self.final_thickness,
            "width_final": self.width_final,
            "epsilon_width": self.epsilon_width,
            "burr_factor": self.burr_factor,
            "defect_risk": self.defect_risk,
        }