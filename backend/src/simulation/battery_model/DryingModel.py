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

    def area(self, params):
        return params.coating_width * 1  # length = 1m

    def evaporation_rate(self, params):
        k0 = 0.001
        mass_transfer_coeff = k0 * (params.V_air / (params.coating_width * params.h_air))
        C_surface = 1.0
        C_air = params.H_air / 100
        return mass_transfer_coeff * self.area(params) * (C_surface - C_air)

    def calculate_dry_thickness(self):
        return self.wet_thickness * self.solid_content

    def calculate_initial_solvent_mass(self, params):
        return self.wet_thickness * (1 - self.solid_content) * params.density

    def time_steps(self, params):
        residence_time = params.drying_length / params.web_speed
        return int(residence_time / params.delta_t)

    def update_properties(self, params):
        evap_rate = self.evaporation_rate(params)
        if self.M_solvent == 0:  # init
            self.M_solvent = self.calculate_initial_solvent_mass(params)

        self.M_solvent -= (evap_rate / self.area(params)) * params.delta_t
        self.M_solvent = max(self.M_solvent, 0)

        self.dry_thickness = self.calculate_dry_thickness()
        self.defect_risk = abs(evap_rate / self.area(params)) > params.max_safe_evap_rate

    def get_properties(self):
        return {
            "wet_thickness": float(self.wet_thickness),
            "dry_thickness": float(self.dry_thickness),
            "M_solvent": float(self.M_solvent),
            "defect_risk": bool(self.defect_risk),
            "solid_content": float(self.solid_content),
        }

