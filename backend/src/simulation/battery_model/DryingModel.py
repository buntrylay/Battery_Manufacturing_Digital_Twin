from simulation.battery_model.BaseModel import BaseModel
from simulation.battery_model.CoatingModel import CoatingModel


class DryingModel(BaseModel):
    def __init__(self, coating_model: CoatingModel):
        # from coating
        self.wet_thickness = coating_model.wet_thickness
        self.solid_content = coating_model.solid_content

        # outputs
        self.dry_thickness = 0
        self.M_solvent = 0
        self.defect_risk = False

        # constants
        self.coating_width = 0.5
        self.density = 1500
        self.solvent_density = 800
        self.delta_t = 1
        self.max_safe_evap_rate = 0.004

    def area(self, params):
        return self.coating_width * 1  # length = 1m

    def evaporation_rate(self, V_air, coating_width, h_air, H_air):
        k0 = 0.001
        mass_transfer_coeff = k0 * (V_air / (coating_width * h_air))
        C_surface = 1.0
        C_air = H_air / 100
        return mass_transfer_coeff * self.area(coating_width) * (C_surface - C_air)

    def calculate_dry_thickness(self, wet_thickness, solid_content):
        return wet_thickness * solid_content

    def calculate_solvent_mass(self, wet_thickness, solid_content, density):
        return wet_thickness * (1 - solid_content) * density

    def time_steps(self, drying_length, web_speed, delta_t):
        residence_time = drying_length / web_speed
        return int(residence_time / delta_t)

    def update_properties(self, params):
        evap_rate = self.evaporation_rate(params.V_air, params.coating_width, params.h_air, params.H_air)
        if self.M_solvent == 0:  # init
            self.M_solvent = self.calculate_solvent_mass(
                self.wet_thickness, self.solid_content, params.density
            )
        self.M_solvent -= (evap_rate / self.area(params.coating_width)) * params.delta_t
        self.M_solvent = max(self.M_solvent, 0)
        self.dry_thickness = self.calculate_dry_thickness(self.wet_thickness, self.solid_content)
        self.defect_risk = (abs(evap_rate / self.area(params.coating_width)) > params.max_safe_evap_rate)

    def get_properties(self):
        return {
            "wet_thickness": float(self.wet_thickness),
            "dry_thickness": float(self.dry_thickness),
            "M_solvent": float(self.M_solvent),
            "defect_risk": bool(self.defect_risk),
            "solid_content": float(self.solid_content),
        }
