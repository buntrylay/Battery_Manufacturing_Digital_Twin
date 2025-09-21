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
        self.H_air = 80.0
        self.COATING_WIDTH = 0.5
        self.DENSITY = 1500
        self.DELTA_T = 1
        self.SOLVENT_DENSITY = 800
        self.MAX_SAFE_EVAP_RATE = 0.004
        self.AREA = self.COATING_WIDTH * 1  # length = 1m
        self.drying_length = 10

    def evaporation_rate(self):
        k0 = 0.001
        mass_transfer_coeff = k0 * (self.V_air / (self.COATING_WIDTH * self.H_air))
        C_surface = 1.0
        C_air = self.H_air / 100
        return mass_transfer_coeff * self.AREA * (C_surface - C_air)

    def calculate_dry_thickness(self, wet_thickness, solid_content):
        return self.wet_thickness * self.solid_content

    def calculate_initial_solvent_mass(self, wet_thickness, solid_content, density):
        return self.wet_thickness * (1 - self.solid_content) * self.DENSITY

    def time_steps(self, web_speed, delta_t=1):
        residence_time = self.drying_length / web_speed
        return int(residence_time / delta_t)

    def update_properties(self, params):
        evap_rate = self.evaporation_rate()

        if self.M_solvent == 0:
            self.M_solvent = self.calculate_initial_solvent_mass(
                self.wet_thickness, self.solid_content, self.DENSITY
            )

        self.M_solvent -= (evap_rate / self.AREA) * self.DELTA_T
        self.M_solvent = max(self.M_solvent, 0)

        self.dry_thickness = self.calculate_dry_thickness(self.wet_thickness, self.solid_content)
        self.defect_risk = abs(evap_rate / self.AREA) > self.MAX_SAFE_EVAP_RATE


    def get_properties(self):
        return {
            "wet_thickness": float(self.wet_thickness),
            "dry_thickness": float(self.dry_thickness),
            "M_solvent": float(self.M_solvent),
            "defect_risk": bool(self.defect_risk),
            "solid_content": float(self.solid_content),
        }
