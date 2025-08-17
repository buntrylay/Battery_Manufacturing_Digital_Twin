class DryingPropertyCalculator:
    """
    Calculates drying-related properties for battery electrode manufacturing.
    Used to estimate evaporation rates, thickness changes, and process timing.
    """

    def __init__(self):
        # Physical and process parameters
        self.coating_width = 0.5          # Width of coating (m)
        self.h_air = 0.1                  # Air gap height (m)
        self.drying_length = 10           # Length of drying section (m)
        self.T_dry = 100                  # Drying temperature (°C)
        self.V_air = 1.0                  # Air velocity (m/s)
        self.H_air = 80                   # Air humidity (%)
        self.density = 1500               # Coating density (kg/m³)
        self.solvent_density = 800        # Solvent density (kg/m³)
        self.k0 = 0.001                   # Base mass transfer coefficient
        self.delta_t = 1                  # Time step (s)
        self.max_safe_evap_rate = 0.004   # Max safe evaporation rate (kg/s)

    def area(self):
        """
        Returns the area considered for drying (m²).
        Assumes a length of 1 m for calculation.
        """
        return self.coating_width * 1 

    def evaporation_rate(self):
        """
        Calculates the evaporation rate (kg/s) based on mass transfer.

        Returns:
            float: Estimated evaporation rate (kg/s)
        """
        mass_transfer_coeff = self.k0 * (self.V_air / (self.coating_width * self.h_air))
        C_surface = 1.0
        C_air = self.H_air / 100
        return mass_transfer_coeff * self.area() * (C_surface - C_air)

    def calculate_dry_thickness(self, wet_thickness, solid_content):
        """
        Calculates dry coating thickness from wet thickness and solid content.

        Parameters:
            wet_thickness (float): Initial wet coating thickness (m)
            solid_content (float): Fraction of solids in slurry (0-1)

        Returns:
            float: Dry coating thickness (m)
        """
        return wet_thickness * solid_content

    def calculate_initial_solvent_mass(self, wet_thickness, solid_content):
        """
        Calculates initial solvent mass per unit area.

        Parameters:
            wet_thickness (float): Initial wet coating thickness (m)
            solid_content (float): Fraction of solids in slurry (0-1)

        Returns:
            float: Initial solvent mass per unit area (kg/m²)
        """
        return wet_thickness * (1 - solid_content) * self.density

    def time_steps(self, web_speed):
        """
        Calculates the number of time steps for a web to pass through the dryer.

        Parameters:
            web_speed (float): Speed of the web (m/s)
                (web = continuous sheet of coated material moving through the line)

        Returns:
            int: Number of simulation time steps for drying
        
        web -  the continuous sheet of coated material (such as a metal foil coated with electrode slurry) that moves through the production line
        """
        residence_time = self.drying_length / web_speed
        return int(residence_time / self.delta_t)