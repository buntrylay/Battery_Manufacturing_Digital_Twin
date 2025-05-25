class DryingPropertyCalculator:
    def __init__(self):
        self.coating_width = 0.5      # m
        self.h_air = 0.1              # m
        self.drying_length = 10       # m
        self.T_dry = 100              # °C
        self.V_air = 1.0              # m/s
        self.H_air = 80               # %
        self.density = 1500           # kg/m³
        self.solvent_density = 800    # kg/m³
        self.k0 = 0.001               # base mass transfer coefficient
        self.delta_t = 1              # s
        self.max_safe_evap_rate = 0.004  # kg/s

    def area(self):
        return self.coating_width * 1  # length = 1m

    def evaporation_rate(self):
        mass_transfer_coeff = self.k0 * (self.V_air / (self.coating_width * self.h_air))
        C_surface = 1.0
        C_air = self.H_air / 100
        return mass_transfer_coeff * self.area() * (C_surface - C_air)

    def calculate_dry_thickness(self, wet_thickness, solid_content):
        return wet_thickness * solid_content

    def calculate_initial_solvent_mass(self, wet_thickness, solid_content):
        return wet_thickness * (1 - solid_content) * self.density

    def time_steps(self, web_speed):
        residence_time = self.drying_length / web_speed
        return int(residence_time / self.delta_t)