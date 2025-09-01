from simulation.battery_model.MixingModel import MixingModel
from simulation.battery_model.BaseModel import BaseModel
import numpy as np
import random

class CoatingModel(BaseModel):
    def __init__(self, mixing_model: MixingModel):
        # Passed from mixing model
        total_solids = mixing_model.AM + mixing_model.CA + mixing_model.PVDF
        total_volume = total_solids + mixing_model.solvent
        self.electrode_type = mixing_model.electrode_type
        self.solid_content = total_solids / total_volume if total_volume > 0 else 0

        # Base viscosity from mixing
        self.base_viscosity = mixing_model.viscosity

        # Calculated properties
        self.temperature = 25  # default starting temperature
        self.viscosity = self.base_viscosity
        self.wet_thickness = 0
        self.dry_thickness = 0
        self.defect_risk = False
        self.shear_rate = 0
        self.uniformity = 1.0  # 1 = perfect uniformity

    def update_temperature(self):
        """
        Update the temperature to simulate fluctuation (random between 24 and 26°C)
        """
        self.temperature = random.uniform(23, 27)

    def calculate_viscosity_temp_adjusted(self):
        """
        Adjust viscosity based on coating temperature using an exponential relation.
        """
        k_vis = 0.1  # temperature sensitivity coefficient
        self.viscosity = self.base_viscosity * np.exp(-k_vis * (25 - self.temperature))

    def calculate_wet_thickness(self, flow_rate, coating_speed, coating_width):
        return flow_rate / (coating_speed * coating_width) * (25 / self.temperature)
 
    def calculate_dry_thickness(self, wet_thickness, solid_content):
        # Optional: include slight evaporation effect
        evap_factor = 1 + 0.01 * (self.temperature - 25)
        return wet_thickness * solid_content / evap_factor

    def calculate_shear_rate(self, coating_speed, gap_height):
        self.shear_rate = coating_speed / gap_height
        return self.shear_rate

    def calculate_uniformity(self):
        # simple proxy: higher viscosity improves uniformity to a point
        # normalized between 0.5 and 1.0 for simulation
        self.uniformity = min(max(self.viscosity / 50, 0.5), 1.0)
        return self.uniformity

    def calculate_defect_risk(self, coating_speed, gap_height):
        K = 100
        risk = (coating_speed / gap_height) / (K * self.viscosity)

        if self.temperature < 23.5:
            risk *= 1.2
        elif self.temperature > 26.5:
            risk *= 1.3

        risk /= self.uniformity

        return bool(risk > 1)  # ensure plain Python bool


    def update_properties(self, flow_rate, coating_speed, coating_width, gap_height):
        """
        Update all computed properties dynamically.
        """
        self.update_temperature()
        self.calculate_viscosity_temp_adjusted()
        self.wet_thickness = self.calculate_wet_thickness(flow_rate, coating_speed, coating_width)
        self.dry_thickness = self.calculate_dry_thickness(self.wet_thickness, self.solid_content)
        self.calculate_shear_rate(coating_speed, gap_height)
        self.calculate_uniformity()
        self.defect_risk = bool(self.calculate_defect_risk(coating_speed, gap_height))

    def get_properties(self):
        return {
            "temperature": round(self.temperature, 2),
            "solid_content": self.solid_content,
            "viscosity": round(self.viscosity, 4),
            "wet_thickness": round(self.wet_thickness, 4),
            "dry_thickness": round(self.dry_thickness, 4),
            "shear_rate": round(self.shear_rate, 4),
            "uniformity": round(self.uniformity, 4),
            "defect_risk": self.defect_risk,
        }
