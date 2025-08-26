from simulation.machine.BaseMachine import BaseMachine
from simulation.sensor.CalendaringProcess import CalendaringProcess
from datetime import datetime, timedelta
import threading
import time
import json
import os

class CalendaringMachine(BaseMachine):
    """
    Simulates the calendaring process in battery manufacturing.
    Compresses dry electrodes to reduce porosity and achieve desired thickness.
    """

    def __init__(self, id, machine_parameters: dict):
        super().__init__(id)
        self.name = "CalendaringMachine"
        self.start_datetime = datetime.now()
        self.total_time = 0
        self.lock = threading.Lock()

        # Create output directory
        self.output_dir = os.path.join(os.getcwd(), "calendaring_output")
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory created at: {self.output_dir}")

        # Process Parameters
        self.h_roll_initial = machine_parameters["roll_gap"]           # Initial roll gap (m)
        self.P_roll = machine_parameters["roll_pressure"]      # Initial pressure (Pa)
        self.v_roll = machine_parameters["roll_speed"]         # Initial speed (m/s)
        self.delta_dry = None  # From drying stage (m)
        self.phi_initial = 0.45  # Initial porosity
        self.T = machine_parameters.get("temperature", 25)     # Environment temperature (°C)
        self.h_roll = self.h_roll_initial
        # Calculations
        self.calculator = CalendaringProcess()

    def _format_result(self, step=None, is_final=False):
        """
        Format the current or final process data as a dictionary.
        """
        with self.lock:
            base = {
                "TimeStamp": (self.start_datetime + timedelta(seconds=self.total_time)).isoformat(),
                "Duration": round(self.total_time, 5),
                "Machine ID": self.id,
                "Process": "Calendaring"
            }
            
            properties = {
                "roll_gap_m": round(self.h_roll, 8),
                "roll_speed_m_per_s": round(self.v_roll, 4),
                "applied_pressure_Pa": round(self.P_roll, 2),
                "strain_epsilon": round(self.epsilon_val, 6),
                "calculated_stress_Pa": round(self.sigma_theory, 2),
                "final_thickness_m": round(self.final_thickness, 8),
                "porosity_after_calendaring": round(self.porosity, 4),
                "defect_risk": self.risk
            }
            
            if is_final:
                base["Final Properties"] = properties
            else:
                base.update(properties)

            return base

    def _write_json(self, data, filename):
        try:
            timestamp = data["TimeStamp"].replace(":", "-").replace(".", "-")
            unique_filename = f"calendaring_output/{self.id}_{timestamp}_{filename}"
            with open(unique_filename, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Results saved to {unique_filename}")
        except Exception as e:
            print(f"Error writing result to file: {e}")

    def _simulate(self, end_time=60, interval=1):
        last_saved_time = time.time()
        last_saved_result = None

        for t in range(0, end_time + 1, interval):
            self.total_time = t

            self.epsilon_val = self.calculator._epsilon(self.delta_dry, self.h_roll)
            self.sigma_theory = self.calculator._sigma_calc(self.epsilon_val)
            self.porosity = self.calculator._porosity_reduction(self.epsilon_val, self.phi_initial)
            self.final_thickness = self.h_roll
            self.risk, self.warning_msg = self.calculator._defect_risk(self.P_roll, self.sigma_theory, t)

            result = self._format_result()

            # Save periodically
            now = time.time()
            if now - last_saved_time >= 0.1 and result != last_saved_result:
                filename = f"result_at_{round(self.total_time)}s.json"
                self._write_json(result, filename)
                last_saved_result = result
                last_saved_time = now

            time.sleep(0.1)

    def run(self):
        """
        Run the calendaring simulation.
        """
        if self.state:
            self._simulate()
            thread_broadcast(f"Calendaring process {self.id} in progress...") # Broadcast continuation message
            final_result = self._format_result(is_final=True)
            filename = f"final_results_{self.id}.json"
            self._write_json(final_result, filename)
            print(f"Calendaring process completed on {self.id}\n")
    
    def update_from_drying(self, dry_thickness_drying):
        with self.lock:
            self.delta_dry = dry_thickness_drying
            print(f"{self.id}: Received from drying - dry_thickness={dry_thickness_drying}")
            
    def get_final_calendaring(self):
        with self.lock:
            return {
                "delta_cal_cal": self.final_thickness,
                "porosity_cal": self.porosity,
                "web_speed_cal": self.v_roll,
                "stiffness_cal": self.calculator.E,
                "final_thickness_m" : self.final_thickness
            }