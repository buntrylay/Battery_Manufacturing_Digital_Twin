import os
import json
import time
import threading
from datetime import datetime, timedelta
from simulation.machine.BaseMachine import BaseMachine
from simulation.sensor.AgingPropertyCalculator import AgingPropertyCalculator

class AgingMachine(BaseMachine):

    def __init__(self, id, machine_parameters: dict):
        super().__init__(id)
        self.name = "AgingMachine"
        self.start_datetime = datetime.now()
        self.total_time = 0
        self.lock = threading.Lock()
        self.is_on = True

        self.output_dir = os.path.join(os.getcwd(), "aging_output")
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory created at: {self.output_dir}")

        self.SOC_0 = machine_parameters["SOC_0"]
        self.Q_cell = machine_parameters["Q_cell"]
        self.V_OCV = machine_parameters["V_OCV(0)"]
        self.k_leak = machine_parameters["k_leak"]
        self.T = machine_parameters["temperature"]
        self.t_aging = machine_parameters["aging_time_days"]
        self.delta_t = 3600  # 1 hour step

        self.calculator = AgingPropertyCalculator()

    def update_from_formation_cycling(self, formation_data):
        with self.lock:
            self.SOC = formation_data.get("SOC_0", self.SOC_0)
            self.Q_cell = formation_data.get("Q_cell", self.Q_cell)
            self.V_OCV = formation_data.get("V_OCV", self.V_OCV)
            self.k_leak = formation_data.get("k_leak", self.k_leak)
            self.T = formation_data.get("temperature", self.T)

    def _format_result(self, step=None, is_final=False):
        with self.lock:
            base = {
                "TimeStamp": (self.start_datetime + timedelta(seconds=self.total_time)).isoformat(),
                "Duration (days)": round(self.total_time / 86400, 2),
                "Machine ID": self.id,
                "Process": self.name
            }
            properties = {
                "Initial SOC": self.SOC_0,
                "Temperature (C)": self.T,
                "Final SOC (%)": round(self.SOC * 100, 2),
                "Final OCV (V)": round(self.V_OCV, 4),
                "Leakage Current (mA)": round(self.I_leak * 1000, 4)
            }

            if is_final:
                base["Final Properties"] = properties
            else:
                base.update(properties)

            return base

    def _write_json(self, data, filename):
        try:
            timestamp = data["TimeStamp"].replace(":", "-").replace(".", "-")
            unique_filename = os.path.join(self.output_dir, f"{self.id}_{timestamp}_{filename}")
            with open(unique_filename, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Results saved to {unique_filename}")
        except Exception as e:
            print(f"Error writing result: {e}")

    def _simulate(self, t_aging, delta_t):
        total_seconds = int(self.t_aging * 24 * 3600)

        if None in [self.SOC_0, self.Q_cell, self.V_OCV, self.k_leak, self.T]:
            raise ValueError("Required inputs are missing before simulation.")

        last_saved_time = time.time()
        last_saved_result = None

        self.SOC = self.SOC_0
        self.V_OCV = self.calculator.ocv_drift(self.SOC)
        self.I_leak = self.calculator.leakage_current(self.k_leak)

        for t in range(0, int(t_aging * 24 * 3600) + 1, delta_t):
            self.total_time = t
            self.SOC = self.calculator.soc_delay(self.SOC_0, self.k_leak, t)
            self.V_OCV = self.calculator.ocv_drift(self.SOC)
            self.I_leak = self.calculator.leakage_current(self.k_leak)

            output = self._format_result()
            now = time.time()
            if now - last_saved_time >= 0.1 and output != last_saved_result:
                filename = f"result_at_{round(self.total_time)}s.json"
                self._write_json(output, filename)
                last_saved_result = output
                last_saved_time = now
            time.sleep(0.01)

        final_output = self._format_result(is_final=True)
        self._write_json(final_output, "final_result.json")

    def run(self):
        if self.is_on:
            try:
                self._simulate(self.t_aging, self.delta_t)
                print(f"Aging process completed on {self.id}")
            except Exception as e:
                print(f"Error during aging process on {self.id}: {e}")
