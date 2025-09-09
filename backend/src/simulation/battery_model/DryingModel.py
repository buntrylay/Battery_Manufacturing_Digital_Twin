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
        self.V_air = 1.0
        self.T_dry = 100
        self.H_air = 80
        self.h_air = 0.1
        self.drying_length = 10
        self.coating_width = 0.5
        self.density = 1500
        self.solvent_density = 800
        self.delta_t = 1
        self.max_safe_evap_rate = 0.004

    def evaporation_rate(self, V_air, H_air, coating_width, area):
        k0 = 0.001
        mass_transfer_coeff = k0 * (V_air / (coating_width * H_air))
        C_surface = 1.0
        C_air = H_air / 100
        return mass_transfer_coeff * area * (C_surface - C_air)

    def calculate_dry_thickness(self, wet_thickness, solid_content):
        return wet_thickness * solid_content

    def calculate_initial_solvent_mass(self, wet_thickness, solid_content, density):
        return wet_thickness * (1 - solid_content) * density

    def time_steps(self, drying_length, web_speed, delta_t=1):
        residence_time = drying_length / web_speed
        return int(residence_time / delta_t)

    def update_properties(self, params):
        evap_rate = self.evaporation_rate(params.V_air, params.H_air, self.COATING_WIDTH, self.AREA)
        if self.M_solvent == 0:  # initialise a solvent mass
            self.M_solvent = self.calculate_initial_solvent_mass(params.wet_thickness, params.solid_content, self.DENSITY)
        self.M_solvent -= (evap_rate / self.AREA) * self.DELTA_T
        self.M_solvent = max(self.M_solvent, 0)
        self.dry_thickness = self.calculate_dry_thickness(params.wet_thickness, params.solid_content)
        self.defect_risk = abs(evap_rate / self.AREA) > self.MAX_SAFE_EVAP_RATE

    def get_properties(self):
        return {
            "wet_thickness": float(self.wet_thickness),
            "dry_thickness": float(self.dry_thickness),
            "M_solvent": float(self.M_solvent),
            "defect_risk": bool(self.defect_risk),
            "solid_content": float(self.solid_content),
        }
