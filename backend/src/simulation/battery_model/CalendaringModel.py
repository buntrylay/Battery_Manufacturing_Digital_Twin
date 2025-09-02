from dataclasses import dataclass
from simulation.battery_model.BaseModel import BaseModel
from simulation.battery_model.DryingModel import DryingModel
import numpy as np


class CalendaringModel(BaseModel):
    def __init__(self, drying_model: DryingModel, initial_porosity: float):
        # from drying
        self.dry_thickness = drying_model.dry_thickness
        self.initial_porosity = initial_porosity

        # state
        self.final_thickness = 0
        self.porosity = 0
        self.defect_risk = False
        self.epsilon_val = 0
        self.sigma_theory = 0

        # material constant
        self.E = 500e6  # Elastic modulus (Pa)
        self.k_p = 3.0  # Porosity reduction constant

    def epsilon(self, h_roll):
        return (self.dry_thickness - h_roll) / self.dry_thickness

    def sigma_calc(self, epsilon_val):
        return self.E * epsilon_val

    def porosity_reduction(self, epsilon_val):
        return self.initial_porosity * np.exp(-self.k_p * epsilon_val)

    def defect_check(self, applied_sigma, theoretical_sigma):
        return applied_sigma > 2 * theoretical_sigma

    def update_properties(self, params):
        self.epsilon_val = self.epsilon(params.roll_gap)
        self.sigma_theory = self.sigma_calc(self.epsilon_val)
        self.porosity = self.porosity_reduction(self.epsilon_val)
        self.final_thickness = params.roll_gap
        self.defect_risk = self.defect_check(params.roll_pressure, self.sigma_theory)

    def get_properties(self):
        return {
            "final_thickness": self.final_thickness,
            "porosity": self.porosity,
            "defect_risk": self.defect_risk,
        }
