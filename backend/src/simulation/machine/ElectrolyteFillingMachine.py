import os
import json
import time
import threading
from datetime import datetime, timedelta
from simulation.machine.BaseMachine import BaseMachine
from simulation.sensor.ElectrolyteFillingProcess import ElectrolyteFillingCalculation


class ElectrolyteFillingMachine(BaseMachine):

    def __init__(self, id, machine_parameter: dict):
        super().__init__(id)
        self.name = "ElectrolyteFillingMachine"
        self.start_datetime = datetime.now()

        self.total_time = 0
        self.t = 0
        self.lock = threading.Lock()
        self.is_on = True  # Ensure this flag is initialized

        # Ensure output directory exists
        self.output_dir = os.path.join(os.getcwd(), "filling_output")
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory created at: {self.output_dir}")

        # Initialize machine parameters
        self.P_vac = machine_parameter["Vacuum_level"]
        self.P_fill = machine_parameter["Vacuum_filling"]
        self.T_soak = machine_parameter["Soaking_time"]

        self.phi_final = None
        self.calculator = ElectrolyteFillingCalculation()

        # Attributes expected from rewind
        self.epsilon_width = None
        self.length = None
        self.width = None
        self.thickness = None

    def update_from_rewind(self, rewind_data):
        with self.lock:
            self.phi_final = rewind_data.get("phi_final")
            self.length = rewind_data.get("wound_length")
            self.epsilon_width = rewind_data.get("epsilon_width")
            self.width = rewind_data.get("final_width")
            self.thickness = rewind_data.get("final_thickness_m")

    def _format_result(self, step=None, is_final=False):
        with self.lock:
            base = {
                "TimeStamp": (self.start_datetime + timedelta(seconds=self.total_time)).isoformat(),
                "Duration": round(self.total_time, 5),
                "Machine ID": self.id,
                "Process": "Electrolyte Filling"
            }
            properties = {
                "Vacuum Level": self.P_vac,
                "Vacuum Filling": self.P_fill,
                "Soaking Time": self.T_soak,
                "Volume Electrolyte_cm3": round(self.V_elec),
                "Electrolyte Density": round(self.phi_elec),
                "Total Volume": round(self.V_max),
                "Wetness": round(self.eta_wetting),
                "Filling Volume": round(self.V_elec_filling),
                "Defect Risk": self.defect_risk
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

    def _simulate(self, end_time=100, t=1):
        if None in [self.length, self.width, self.thickness, self.phi_final]:
            raise ValueError("Required rewind inputs are missing before simulation.")

        last_saved_time = time.time()
        last_saved_result = None

        # Initial calculations
        self.V_sep = self.calculator.V_sep()
        self.V_elec = self.calculator.V_elec(self.length, self.width, self.thickness)
        self.phi_elec = self.calculator.phi_elec()
        self.V_max = self.calculator.V_max(self.phi_final, self.V_elec, self.V_sep)
        self.eta_wetting = self.calculator.eta_wetting(self.t)
        self.V_elec_filling = self.calculator.V_elec_filling(self.eta_wetting, self.V_max)
        self.defect_risk = self.calculator.defect_risk(self.V_elec_filling, self.V_max)
        
        for t in range(0, end_time + 1, t):
            self.total_time = t
            self.eta_wetting = self.calculator.eta_wetting(t)
            self.V_elec_filling = self.calculator.V_elec_filling(self.eta_wetting, self.V_max)
            self.defect_risk = self.calculator.defect_risk(self.V_elec_filling, self.V_max)

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
            try:
                self._simulate()
                print(f"Electrolyte Filling process completed on {self.id}")
            except Exception as e:
                print(f"Simulation error on {self.id}: {e}")
                
    def get_final_filling(self):
        with self.lock:
            return {
                "volume_electrolyte" : self.V_max,
                "wetting_efficiency": self.eta_wetting
            }