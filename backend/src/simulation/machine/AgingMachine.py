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

        self.SOC_0 = None
        self.Q_cell = None
        self.V_OCV = None
        self.k_leak = machine_parameters.get("k_leak")
        self.T = machine_parameters.get("temperature")
        self.t_aging = machine_parameters.get("aging_time_days")
        self.delta_t = 3600  # 1 hour step

        self.calculator = AgingPropertyCalculator()

    def update_from_formation_cycling(self, formation_data: dict):
        with self.lock:
            self.SOC_0 = formation_data.get("final_sei_efficiency", self.SOC_0)
            self.Q_cell = formation_data.get("final_cell_capacity_Ah", self.Q_cell)
            self.V_OCV = formation_data.get("final_voltage_V", self.V_OCV)

    def _format_result(self, step=None, is_final=False):
        with self.lock:
            base = {
                "TimeStamp": (
                    self.start_datetime + timedelta(seconds=self.total_time)
                ).isoformat(),
                "Duration (days)": round(self.total_time / 86400, 2),
                "Machine ID": self.id,
                "Process": self.name,
            }
            properties = {
                "Initial SOC": self.SOC_0,
                "Temperature (C)": self.T,
                "Final SOC (%)": round(self.SOC * 100, 2),
                "Final OCV (V)": round(self.V_OCV, 4),
                "Leakage Current (mA)": round(self.I_leak * 1000, 4),
            }

            if is_final:
                base["Final Properties"] = properties
            else:
                base.update(properties)

            return base

    def _write_json(self, data, filename):
        try:
            timestamp = data["TimeStamp"].replace(":", "-").replace(".", "-")
            unique_filename = os.path.join(
                self.output_dir, f"{self.id}_{timestamp}_{filename}"
            )
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
        self.V_OCV = self.calculator.ocv_drift(self.SOC_0)
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
        defects = self.assess_defect_risk(self.SOC, self.V_OCV, self.I_leak)
        final_output["defect_risk"] = defects
        self._write_json(final_output, "final_result.json")

    def assess_defect_risk(self, final_soc, final_ocv, final_i_leak):
        return {
            "OCV_Drop": bool((self.V_OCV - final_ocv) > 0.1),
            "Leakage_Current_High": bool(final_i_leak > 0.0001),
            "SOC_Loss": bool(final_soc < 0.95 * self.SOC_0),
        }

    def get_process_properties(self):
        return {
            "Initial SOC": self.SOC_0,
            "Temperature (C)": self.T,
            "Final SOC (%)": round(self.SOC * 100, 2),
            "Final OCV (V)": round(self.V_OCV, 4),
            "Leakage Current (mA)": round(self.I_leak * 1000, 4),
        }

    def run(self):
        if self.is_on:
            try:
                self._simulate(self.t_aging, self.delta_t)
                print(f"Aging process completed on {self.id}")
            except Exception as e:
                print(f"Error during aging process on {self.id}: {e}")
