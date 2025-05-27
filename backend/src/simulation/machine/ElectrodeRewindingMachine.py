import time
import json
import os
import numpy as np
from datetime import datetime, timedelta
from simulation.machine.BaseMachine import BaseMachine
from simulation.sensor.ElectrodeRewindingPropertyCalculator import RewindingPropertyCalculator

class RewindingMachine(BaseMachine):
    def __init__(self, id, machine_parameters: dict):
        super().__init__(id)
        self.name = "RewindingMachine"
        self.start_datetime = datetime.now()
        self.total_time = 0

        self.output_dir = os.path.join(os.getcwd(), "rewinding_output")
        os.makedirs(self.output_dir, exist_ok=True)

        # Inputs from inspection or setup
        self.delta_cal = None
        self.D_core = machine_parameters["core_diameter"]
        self.tau_initial = machine_parameters["initial_tension"]
        self.n_taper = machine_parameters.get("taper_factor", 1.0)
        self.v_rewind = machine_parameters["rewind_speed"]
        self.H_env = machine_parameters["humidity"]

        # Simulation state
        self.L_wound = 0

        self.time_series = []
        self.D_roll_series = []
        self.tau_series = []
        self.H_roll_series = []

    def _simulate(self, total_time=120, delta_t=1):
        for t in range(0, total_time + 1, delta_t):
            self.total_time = t
            self.L_wound += self.v_rewind * delta_t

            D_roll = np.sqrt(self.D_core**2 + (4 * self.L_wound * self.delta_cal) / np.pi)
            tau_rewind = self.tau_initial * (self.D_core / D_roll)**self.n_taper
            H_roll = tau_rewind / self.delta_cal

            self.time_series.append(t)
            self.D_roll_series.append(D_roll)
            self.tau_series.append(tau_rewind)
            self.H_roll_series.append(H_roll)

            time.sleep(0.05)

    def run(self):
        if self.is_on:
            self._simulate()
            self._save_result()
            print(f"Rewinding process completed on {self.id}\n")

    def _save_result(self):
        data = {
            "TimeStamp": self.start_datetime.isoformat(),
            "Machine ID": self.id,
            "Final Roll Diameter": self.D_roll_series[-1],
            "Final Roll Hardness": self.H_roll_series[-1],
            "Tension Profile": self.tau_series,
        }
        filename = f"{self.output_dir}/{self.id}_final_result.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=4)
