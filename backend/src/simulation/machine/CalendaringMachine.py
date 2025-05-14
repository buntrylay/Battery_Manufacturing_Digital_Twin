import json
import time
import threading
from datetime import datetime, timedelta
import numpy as np
import os

# Simulated input from drying stage
delta_dry_drying = 80e-6  # Dry coating thickness (m)

class CalendaringMachine:
    """
    Simulates the calendaring process in battery manufacturing.
    Compresses the dry electrode using rolls to adjust porosity and thickness.
    """

    def __init__(self, pause_sec=0.1):
        self.name = "CalendaringMachine"
        self.pause_sec = pause_sec
        self.results = []
        self.start_time = datetime.now()
        self.output_path = os.path.join(os.getcwd(), "calendaring_simulation.json")

        # Input from drying stage
        self.delta_dry = delta_dry_drying
        self.phi_initial = 0.4

        # Controlled Constants
        self.E = 500e6         # Elastic modulus (Pa)
        self.k_p = 3.0         # Porosity reduction constant

        # Initial Settings (subject to dynamic change)
        self.h_roll = 60e-6    # Roll gap (m)
        self.P_roll = 50e6     # Applied roll pressure (Pa)
        self.v_roll = 1.0      # Roll speed (m/s)

        # Fixed Environment
        self.T = 25            # Temperature (°C)

        # Timing
        self.total_time = 60   # Total simulation time (s)
        self.delta_t = 1       # Time step

        # Thread setup
        self.thread = threading.Thread(target=self.run)

    def _epsilon(self):
        return (self.delta_dry - self.h_roll) / self.delta_dry

    def _sigma_calc(self, epsilon_val):
        return self.E * epsilon_val

    def _porosity_reduction(self, epsilon_val):
        return self.phi_initial * np.exp(-self.k_p * epsilon_val)

    def _defect_risk(self, applied_sigma, theoretical_sigma, time_step):
        if applied_sigma > 2 * theoretical_sigma:
            return True, f"Warning: Excessive pressure at t = {time_step}s may cause cracks."
        return False, ""

    def _format_result(self, t, epsilon_val, sigma_val, sigma_theory, porosity, final_thick, risk, warning_msg):
        timestamp = self.start_time + timedelta(seconds=t)
        result = {
            "timestamp": str(timestamp),
            "time_elapsed_s": t,
            "gap": round(self.h_roll, 8),
            "speed": round(self.v_roll, 4),
            "pressure": round(self.P_roll, 2),
            "strain_epsilon": round(epsilon_val, 6),
            "applied_pressure_Pa": round(sigma_val, 2),
            "calculated_stress_Pa": round(sigma_theory, 2),
            "final_thickness_m": round(final_thick, 8),
            "porosity_after_calendaring": round(porosity, 4),
            "defect_risk": risk
        }
        if warning_msg:
            result["warning"] = warning_msg
        return result

    def _print_result(self, result):
        print(json.dumps(result, indent=2))

    def _write_json(self):
        with open(self.output_path, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n[Saved] Simulation results written to {self.output_path}")

    def run(self, step_percent=1):
        steps = int(self.total_time * (step_percent / 100)) or 1
        for t in range(0, self.total_time + 1, steps):
            # Dynamically adjust process parameters
            self.h_roll = 60e-6 * (1 - t / self.total_time)
            self.v_roll = max(0.5, 1.0 - t / (self.total_time * 2))
            self.P_roll = 50e6 * (1 - self.h_roll / self.delta_dry)

            epsilon_val = self._epsilon()
            sigma_val = self.P_roll
            sigma_theory = self._sigma_calc(epsilon_val)
            porosity = self._porosity_reduction(epsilon_val)
            final_thick = self.h_roll

            risk, warning_msg = self._defect_risk(sigma_val, sigma_theory, t)
            result = self._format_result(t, epsilon_val, sigma_val, sigma_theory, porosity, final_thick, risk, warning_msg)

            self.results.append(result)
            self._print_result(result)

            time.sleep(self.pause_sec)

        self._write_json()
