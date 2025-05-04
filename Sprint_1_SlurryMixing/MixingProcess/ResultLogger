import os
import json

class ResultLogger:
    def __init__(self, results):
        self.results = results

    def save_to_json(self, filename):
        os.makedirs("simulation_output", exist_ok=True)
        with open(filename, "w") as f:
            json.dump(self.results, f, indent=4)

    def print_latest(self):
        if self.results:
            latest = self.results[-1]
            print(f"{latest['Time']} | {latest['Component']} | "
                  f"Density: {latest['Density']} | "
                  f"Viscosity: {latest['Viscosity']} | "
                  f"Yield Stress: {latest['YieldStress']}")