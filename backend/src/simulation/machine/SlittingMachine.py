import time
import os
import json
from datetime import datetime, timedelta
from simulation.machine.BaseMachine import BaseMachine
from simulation.sensor.SlittingPropertyCalculator import SlittingPropertyCalculator
import threading
class SlittingMachine(BaseMachine):
    def __init__(self, id, machine_parameters: dict):
        super().__init__(id)
        self.name = "SlittingMachine"
        self.start_datetime = datetime.now()
        self.total_time = 0
        self.lock = threading.Lock()
        # Create output directory
        self.output_dir = os.path.join(os.getcwd(), "slitting_output")
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory created at: {self.output_dir}")

        # Inputs parameters
        self.delta_cal = None  # Will be filled by CalendaringMachine
        self.w_input = None 
        self.phi_final = None
        self.web_speed = None
        self.stiffness = None
        self.final_thickness_m = None
        self.S = machine_parameters["blade_sharpness"]
        self.v_slit = machine_parameters["slitting_speed"]
        self.w_target = machine_parameters["target_width"]
        self.tau_slit = machine_parameters["slitting_tension"]

        # Connect to calculator
        self.calculator = SlittingPropertyCalculator()

    # format the result
    def _format_result(self, is_final=False):
        """
        Format the current process data as a dictionary.
        """
        base = {
            "TimeStamp": (self.start_datetime + timedelta(seconds=self.total_time)).isoformat(),
            "Duration": round(self.total_time, 5),
            "Machine ID": self.id,
            "Process": "Slitting"
        }

        properties = {
            "input_thickness_mm": self.delta_cal,
            "target_width_mm": self.w_target,
            "final_width_mm": round(self.w_final, 3),
            "cut_accuracy_epsilon_mm": round(self.epsilon_width, 3),
            "burr_factor": round(self.burr_factor, 3),
            "defect_risk": self.defect
        }
        if is_final:
            base["Final Properties"] = properties
        else:
            base.update(properties)

        return base
    def _write_json(self, data, filename):
        try:
            timestamp = data["TimeStamp"].replace(":", "-").replace(".", "-")
            unique_filename = f"{self.output_dir}/{self.id}_{timestamp}_{filename}"
            with open(unique_filename, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Results saved to {unique_filename}")
        except Exception as e:
            print(f"Error writing result to file: {e}")

    def _simulate(self, end_time=30, interval=1):
        last_saved_time = time.time()
        last_saved_result = None

        for t in range(0, end_time + 1, interval):
            self.total_time = t

            self.w_final = self.calculator.simulate_width_variation(self.w_target)
            self.epsilon_width = self.calculator.calculate_cut_accuracy(self.w_final, self.w_target)
            self.burr_factor = self.calculator.calculate_burr_factor(
                S= self.S,
                v_slit= self.v_slit,
                tau_slit= self.tau_slit,
            )
            self.defect = self.calculator.is_defective(
                epsilon_width=self.epsilon_width,
                burr_factor=self.burr_factor,
            )

            result = self._format_result()
            now = time.time()
            if now - last_saved_time >= 0.1 and result != last_saved_result:
                filename = f"result_at_{round(self.total_time)}s.json"
                self._write_json(result, filename)
                last_saved_result = result
                last_saved_time = now

            if self.defect:
                print(f"[WARNING] {self.id}: Defect at t={t}s | ε={self.epsilon_width:.3f} mm | B={self.burr_factor:.2f}")

            time.sleep(0.1)

    def run(self):
        if self.is_on:
            self._simulate()
            print(f"Slitting process completed on {self.id}\n")

    def update_from_calendaring(self, cal_data):
        with self.lock:
            self.delta_cal = cal_data.get("delta_cal_cal")
            self.phi_final = cal_data.get("porosity_cal")
            self.web_speed = cal_data.get("web_speed_cal")
            self.stiffness = cal_data.get("stiffness_cal")
            self.final_thickness_m =cal_data.get("final_thickness_m")
            self.w_input = self.delta_cal * (1 - self.phi_final)
        print(f"[{self.id}] Updated from calendaring: thickness={self.delta_cal}, porosity={self.phi_final}, web_speed={self.web_speed}")

# for electrode inspection
    def get_final_slitting(self):
        return {
            "epsilon_width": self.epsilon_width,
            "burr_factor": self.burr_factor,
            "delta_sl": self.delta_cal,
            "phi_final" : self.phi_final,
            "final_width": self.w_final,
            "final_thickness_m" : self.final_thickness_m
        }