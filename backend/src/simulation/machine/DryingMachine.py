import time
import os
import json
from datetime import datetime, timedelta
from simulation.machine.BaseMachine import BaseMachine

class DryingMachine(BaseMachine):
    """
    Simulates the drying process of coated electrodes by modeling solvent evaporation.
    """

    def __init__(self, id, web_speed, wet_thickness, solid_content):
        super().__init__(id)
        self.id = id
        self.web_speed = web_speed
        self.wet_thickness = wet_thickness
        self.solid_content = solid_content

        # Fixed parameters
        self.coating_width = 0.5  # m
        self.h_air = 0.1  # m
        self.drying_length = 10  # m
        self.T_dry = 100  # °C
        self.V_air = 1.0  # m³/s
        self.H_air = 30  # % RH
        self.density = 1500  # slurry density (kg/m³)
        self.solvent_density = 800  # kg/m³
        self.k0 = 0.001  # base mass transfer coefficient (m/s)
        self.delta_t = 1  # s
        self.max_safe_evap_rate = 0.001  # kg/m²/s

        # Derived constants
        self.mass_transfer_coeff = self.k0 * (self.V_air / (self.coating_width * self.h_air))
        self.C_surface = 1.0
        self.C_air = self.H_air / 100
        self.delta_dry = self.wet_thickness * self.solid_content
        self.M_solvent = self.wet_thickness * (1 - self.solid_content) * self.density  # kg/m²
        self.area = self.coating_width * 1  # 1m length assumption
        self.residence_time = self.drying_length / self.web_speed
        self.time_steps = int(self.residence_time / self.delta_t)

        self.total_time = 0
        self.start_datetime = datetime.now()
        self.results = []

        self.output_dir = os.path.join(os.getcwd(), "simulation_output")
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory created at: {self.output_dir}")

    def _format_result(self, is_final=False):
        result = {
            "TimeStamp": (self.start_datetime + timedelta(seconds=self.total_time)).isoformat(),
            "Duration": self.total_time,
            "Machine ID": self.id,
            "Process": "Drying",
            "Wet Thickness (m)": round(self.wet_thickness, 6),
            "Dry Thickness (m)": round(self.delta_dry, 6),
            "Remaining Solvent (kg/m²)": round(self.M_solvent, 6),
            "Evaporation Rate (kg/s)": round(self._calculate_evaporation_rate(), 6),
            "Coating Thickness (m)": round(self._calculate_total_thickness(), 6),
            "Defect Risk": abs(self._calculate_evaporation_rate() / self.area) > self.max_safe_evap_rate
        }
        return result

    def _write_json(self, data, filename):
        try:
            filepath = os.path.join(self.output_dir, filename)
            with open(filepath, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Results saved to {filepath}")
        except Exception as e:
            print(f"Error writing result to file: {e}")

    def _print_result(self, result):
        print(" | ".join(f"{k}: {v}" for k, v in result.items()))

    def _calculate_evaporation_rate(self):
        return -self.mass_transfer_coeff * self.area * (self.C_surface - self.C_air)

    def _calculate_total_thickness(self):
        return self.delta_dry + (self.M_solvent / self.solvent_density)

    def _save_final_results(self):
        final_result = self._format_result(is_final=True)
        filename = f"final_results_{self.id}.json"
        self._write_json(final_result, filename)

    def run(self):
        if self.is_on:
            for t in range(0, self.time_steps + 1, self.delta_t):
                self.total_time = t

                # Update solvent mass
                evap_rate = self._calculate_evaporation_rate()
                self.M_solvent -= (evap_rate / self.area) * self.delta_t
                self.M_solvent = max(0, self.M_solvent)

                # Format and print result
                result = self._format_result()
                self._print_result(result)

                # Save timestamped result
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                filename = f"{self.id}_{timestamp}_result_at_{t}s.json"
                self._write_json(result, filename)

                self.results.append(result)

                if self.M_solvent <= 0:
                    break

                time.sleep(0.05)

            self._save_final_results()

