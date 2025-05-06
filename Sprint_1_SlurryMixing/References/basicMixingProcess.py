import math
import matplotlib.pyplot as plt
 
def mixing_process_model_dynamic(
    M_solid,           # kg
    M_solvent,         # kg
    N,                 # rpm
    total_time,        # minutes
    D,                 # meters
    V,                 # liters
    delta_t=1,         # time step in minutes
    mu_solvent=0.001,  # Pa.s (default NMP viscosity)
    k_viscosity=0.12,  # solid content - viscosity empirical constant
    alpha_mixing=0.005, # energy efficiency for homogeneity
    K_power=0.2,       # mixer power constant
    h_gap=0.02,        # meters (gap between impeller and wall)
    cp_slurry=2000,    # J/kg.K (specific heat capacity)
    beta_temp_viscosity=0.02 # thermal viscosity coefficient
):
    """
    Simulates the dynamic mixing process for battery slurry preparation.
    Returns time series for solid content, viscosity, homogeneity, and temperature.
    """
    # Step 1: Solid Content (%)
    phi = (M_solid / (M_solid + M_solvent)) * 100
 
    # Step 2: Initial Static Viscosity (Pa.s)
    eta_static_ref = mu_solvent * math.exp(k_viscosity * phi)
    eta_static = eta_static_ref
 
    # Step 3: Initial Conditions
    gamma_dot = (math.pi * D * N) / (60 * h_gap)
    lambda_thin = 0.001
    n_thin = 0.7
    P_mixing = K_power * (N/60)**3 * D**5 * 1e3  # Convert rpm to rps
    m_total = M_solid + M_solvent  # kg
    E_input = 0
    T = 25  # Initial temperature (°C)
 
    # Time series storage
    times = []
    viscosities = []
    homogeneities = []
    temperatures = []
 
    # Dynamic Simulation Loop
    for t_min in range(0, total_time + 1, delta_t):
        t_seconds = delta_t * 60
 
        # Update Energy Input
        E_input += (P_mixing * t_seconds) / V
 
        # Update Homogeneity
        S = 1 - math.exp(-alpha_mixing * E_input)
        S = S * 100  # as %
 
        # Update Temperature
        delta_T = (P_mixing * t_seconds) / (m_total * cp_slurry)
        T += delta_T
 
        # Update Static Viscosity with Temperature Effect
        eta_static = eta_static_ref * math.exp(-beta_temp_viscosity * (T - 25))
 
        # Update Dynamic Viscosity (Shear thinning)
        eta_dynamic = eta_static * (1 + lambda_thin * gamma_dot ** n_thin) ** -1
 
        # Store data
        times.append(t_min)
        viscosities.append(eta_dynamic)
        homogeneities.append(S)
        temperatures.append(T)
 
    return times, viscosities, homogeneities, temperatures
 
# Example usage
if __name__ == "__main__":
    times, viscosities, homogeneities, temperatures = mixing_process_model_dynamic(
        M_solid=50,       # 50 kg solids
        M_solvent=50,     # 50 kg solvent
        N=500,            # 500 rpm
        total_time=60,    # 60 minutes
        D=0.2,            # 20 cm impeller
        V=100             # 100 liters tank
    )
 
    # Plotting results
    plt.figure(figsize=(12, 8))
 
    plt.subplot(3, 1, 1)
    plt.plot(times, viscosities, label='Dynamic Viscosity (Pa.s)')
    plt.ylabel('Viscosity (Pa.s)')
    plt.grid()
    plt.legend()
 
    plt.subplot(3, 1, 2)
    plt.plot(times, homogeneities, label='Homogeneity (%)', color='green')
    plt.ylabel('Homogeneity (%)')
    plt.grid()
    plt.legend()
 
    plt.subplot(3, 1, 3)
    plt.plot(times, temperatures, label='Temperature (°C)', color='red')
    plt.xlabel('Time (minutes)')
    plt.ylabel('Temperature (°C)')
    plt.grid()
    plt.legend()
 
    plt.tight_layout()
    plt.show()