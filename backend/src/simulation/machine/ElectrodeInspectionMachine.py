import os
import json
import time
import threading
from datetime import datetime, timedelta
from simulation.machine.BaseMachine import BaseMachine
from simulation.sensor.ElectrodeInspectionPropertyCalculator import ElectrodeInspectionPropertyCalculator

class ElectrodeInspectionMachine(BaseMachine):
    """
    Simulates electrode inspection after slitting.
    Checks width accuracy, thickness, burr, and surface defect density.
    """

    def __init__(self, id, machine_parameters: dict):
        super().__init__(id)
        self.name = "ElectrodeInspectionMachine"
        self.start_datetime = datetime.now()
        self.total_time = 0
        self.lock = threading.Lock()

        # Create output directory
        self.output_dir = os.path.join(os.getcwd(), "inspection_output")
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory created at: {self.output_dir}")

        # Threshold specifications
        self.epsilon_width_max = machine_parameters["epsilon_width_max"]
        self.epsilon_thickness_max = machine_parameters["epsilon_thickness_max"]
        self.B_max = machine_parameters["B_max"]
        self.D_surface_max = machine_parameters["D_surface_max"]
       

        # Will be filled by SlittingMachine
        self.delta_sl = None
        self.phi_final = None
        self.epsilon_width = None
        self.B = None
        self.final_width = None

        # Calculator
        self.calculator = ElectrodeInspectionPropertyCalculator(
            epsilon_width_max=self.epsilon_width_max,
            epsilon_thickness_max=self.epsilon_thickness_max,
            B_max=self.B_max,
            D_surface_max=self.D_surface_max
        )


    def _format_result(self, step=None, is_final=False):
        base = {
            "TimeStamp": (self.start_datetime + timedelta(seconds=self.total_time)).isoformat(),
            "Duration": round(self.total_time, 5),
            "Machine ID": self.id,
            "Process": "ElectrodeInspection"
        }

        properties = {
            "epsilon_width_mm": round(self.epsilon_width, 4),
            "burr_factor": round(self.B, 3),
            "delta_sl_m": self.delta_sl,
            "delta_measured_m": round(self.delta_measured, 7),
            "epsilon_thickness_m": round(self.epsilon_thickness, 7),
            "defects_detected": self.D_detected,
            "Pass_width": self.Pass_width,
            "Pass_thickness": self.Pass_thickness,
            "Pass_burr": self.Pass_burr,
            "Pass_surface": self.Pass_surface,
            "Overall": self.result
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
            print(f"Error writing inspection result: {e}")

    def _simulate(self, end_time=100, interval=1):
        last_saved_time = time.time()
        last_saved_result = None

        for t in range(0, end_time + 1, interval):
            self.total_time = t

            # Simulated data
            self.delta_measured = self.delta_sl + (1e-6 * (0.5 - time.time() % 1))
            self.D_detected = 1  # Fake fixed value for now

            # Perform inspection
            result = self.calculator.is_pass(
                self.epsilon_width,
                self.delta_measured,
                self.delta_sl,
                self.B,
                self.D_detected
            )

            # Unpack
            self.Pass_width = result["Pass_width"]
            self.Pass_thickness = result["Pass_thickness"]
            self.Pass_burr = result["Pass_burr"]
            self.Pass_surface = result["Pass_surface"]
            self.epsilon_thickness = result["epsilon_thickness"]
            self.result = result["Overall"]

            output = self._format_result()
            now = time.time()
            if now - last_saved_time >= 0.1 and output != last_saved_result:
                filename = f"result_at_{round(self.total_time)}s.json"
                self._write_json(output, filename)
                last_saved_result = output
                last_saved_time = now

            time.sleep(0.1)

    def run(self):
        if self.is_on:
            if None in [self.epsilon_width, self.B]:
                raise ValueError(f"{self.id}: Missing slitting inputs.")
            self._simulate()
            
            print(f"Inspection process completed on {self.id}\n")
            
    def update_from_slitting(self, slitting_data):
        with self.lock:
            self.epsilon_width = slitting_data.get("epsilon_width")
            self.B = slitting_data.get("burr_factor")
            self.delta_sl = slitting_data.get("delta_sl")
            self.phi_final = slitting_data.get("phi_final")
            self.final_width = slitting_data.get("final_width")
            self.final_thickness_m = slitting_data.get("final_thickness_m")
            print(f"{self.id}: Received from slitting - ε={self.epsilon_width}, B={self.B}, δ_cal={self.delta_sl}")
            
    def get_final_inspection(self):
        with self.lock:
            return{
                "delta_el" : self.delta_sl,
                "phi_final" : self.phi_final,
                "final_width": self.final_width,
                "final_thickness_m": self.final_thickness_m,
                "epsilon_width": self.epsilon_width
            }