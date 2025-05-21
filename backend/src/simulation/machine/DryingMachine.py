'''
import json
import time
import os
from datetime import datetime, timedelta
from simulation.machine.BaseMachine import BaseMachine
from simulation.sensor.DryingPropertyCalculator import DryingPropertyCalculator

class DryingMachine(BaseMachine):
    def __init__(self, id, wet_thickness_coating, solid_content, web_speed):
        super().__init__(id)
        self.wet_thickness = wet_thickness_coating
        self.solid_content = solid_content
        self.web_speed = web_speed

        self.output_dir = os.path.join(os.getcwd(), "drying_output")
        os.makedirs(self.output_dir, exist_ok=True)

        self.calculator = DryingPropertyCalculator()

        self.start_time = datetime.now()
        self.total_time = 0
        self.results = []

        self.dry_thickness = self.calculator.calculate_dry_thickness(self.wet_thickness, self.solid_content)
        self.M_solvent = self.calculator.calculate_initial_solvent_mass(self.wet_thickness, self.solid_content)

    def _format_result(self, evap_rate, delta_coat, defect_risk):
        return {
            "TimeStamp": (self.start_time + timedelta(seconds=self.total_time)).isoformat(),
            "Duration": self.total_time,
            "Machine ID": self.id,
            "Process": "Drying",
            "Wet Thickness (m)": round(self.wet_thickness, 6),
            "Dry Thickness (m)": round(self.dry_thickness, 6),
            "Remaining Solvent (kg/m²)": round(self.M_solvent, 6),
            "Evaporation Rate (kg/s)": round(evap_rate, 6),
            "Current Coating Thickness (m)": round(delta_coat, 6),
            "Defect Risk": defect_risk
        }

    def run(self):
        last_saved_time = time.time()
        last_saved_result = None

        for t in range(0, self.calculator.time_steps(self.web_speed) + 1):
            self.total_time = t
            evap_rate = self.calculator.evaporation_rate()
            self.M_solvent -= (evap_rate / self.calculator.area()) * self.calculator.delta_t
            self.M_solvent = max(self.M_solvent, 0)
            delta_coat = self.dry_thickness + (self.M_solvent / self.calculator.solvent_density)
            defect_risk = abs(evap_rate / self.calculator.area()) > self.calculator.max_safe_evap_rate

            result = self._format_result(evap_rate, delta_coat, defect_risk)
            self.results.append(result)

            # OPTIONAL: Save periodic snapshots every 0.1s
            now = time.time()
            if now - last_saved_time >= 0.1 and result != last_saved_result:
                filename = f"{self.id}_result_at_{round(self.total_time)}s.json"
                filepath = os.path.join(self.output_dir, filename)
                with open(filepath, "w") as f:
                    json.dump(result, f, indent=4)
                last_saved_result = result
                last_saved_time = now

            if self.M_solvent == 0:
                break
            time.sleep(0.05)

        # Save final result (match coating format)
        final_result = self._format_result(evap_rate, delta_coat, defect_risk)
        final_path = os.path.join(self.output_dir, f"final_results_{self.id}.json")
        with open(final_path, "w") as f:
            json.dump({"Final Properties": final_result}, f, indent=4)

        print(f"Drying process completed on {self.id}")
'''


import json
import time
import os
from glob import glob
from datetime import datetime, timedelta
from simulation.machine.BaseMachine import BaseMachine
from simulation.sensor.DryingPropertyCalculator import DryingPropertyCalculator

class DryingMachine(BaseMachine):
    def __init__(self, id, wet_thickness_coating=None, solid_content=None, web_speed=0.5):
        super().__init__(id)
        self.wet_thickness = wet_thickness_coating
        self.solid_content = solid_content
        self.web_speed = web_speed

        self.output_dir = os.path.join(os.getcwd(), "drying_output")
        os.makedirs(self.output_dir, exist_ok=True)

        self.calculator = DryingPropertyCalculator()

        self.start_time = datetime.now()
        self.total_time = 0
        self.results = []

        self.dry_thickness = None
        self.M_solvent = None

    def _format_result(self, evap_rate, delta_coat, defect_risk):
        return {
            "TimeStamp": (self.start_time + timedelta(seconds=self.total_time)).isoformat(),
            "Duration": self.total_time,
            "Machine ID": self.id,
            "Process": "Drying",
            "Wet Thickness (m)": round(self.wet_thickness, 6),
            "Dry Thickness (m)": round(self.dry_thickness, 6),
            "Remaining Solvent (kg/m²)": round(self.M_solvent, 6),
            "Evaporation Rate (kg/s)": round(evap_rate, 6),
            "Current Coating Thickness (m)": round(delta_coat, 6),
            "Defect Risk": defect_risk
        }

    def run(self):
        # Delay inputs until coating is ready
        if self.wet_thickness is None or self.solid_content is None:
            electrode_type = "Anode" if "Anode" in self.id else "Cathode"
            coat_id = f"MC_Coat_{electrode_type}"
            waited = 0
            max_wait_time = 10
            while waited < max_wait_time:
                files = sorted(glob(f"coating_output/*final_results_{coat_id}.json"), reverse=True)
                if files:
                    with open(files[0]) as f:
                        data = json.load(f)["Final Properties"]
                        self.wet_thickness = data["wet_thickness_m"]
                        self.solid_content = data["solid_content"]
                        break
                time.sleep(0.5)
                waited += 0.5

            if self.wet_thickness is None or self.solid_content is None:
                raise ValueError(f"[{self.id}] Cannot start drying: wet_thickness or solid_content is still None")

        print(f"[DEBUG] {self.id} - wet_thickness: {self.wet_thickness}, solid_content: {self.solid_content}")
        print(f"Starting drying simulation for {self.id}...")

        self.dry_thickness = self.calculator.calculate_dry_thickness(self.wet_thickness, self.solid_content)
        self.M_solvent = self.calculator.calculate_initial_solvent_mass(self.wet_thickness, self.solid_content)

        last_saved_time = time.time()
        last_saved_result = None

        for t in range(0, self.calculator.time_steps(self.web_speed) + 1):
            self.total_time = t
            evap_rate = self.calculator.evaporation_rate()
            self.M_solvent -= (evap_rate / self.calculator.area()) * self.calculator.delta_t
            self.M_solvent = max(self.M_solvent, 0)
            delta_coat = self.dry_thickness + (self.M_solvent / self.calculator.solvent_density)
            defect_risk = abs(evap_rate / self.calculator.area()) > self.calculator.max_safe_evap_rate

            result = self._format_result(evap_rate, delta_coat, defect_risk)
            self.results.append(result)

            now = time.time()
            if now - last_saved_time >= 0.1 and result != last_saved_result:
                filename = f"{self.id}_result_at_{round(self.total_time)}s.json"
                filepath = os.path.join(self.output_dir, filename)
                with open(filepath, "w") as f:
                    json.dump(result, f, indent=4)
                print(f"[{self.id}] Saved result at t={self.total_time}s | "
                      f"EvapRate={evap_rate:.5f} | RemainingSolvent={self.M_solvent:.4f} | DefectRisk={defect_risk}")
                last_saved_result = result
                last_saved_time = now

            if self.M_solvent == 0:
                print(f"[{self.id}] Solvent fully evaporated at t={self.total_time}s.")
                break
            time.sleep(0.05)

        final_result = self._format_result(evap_rate, delta_coat, defect_risk)
        final_path = os.path.join(self.output_dir, f"final_results_{self.id}.json")
        with open(final_path, "w") as f:
            json.dump({"Final Properties": final_result}, f, indent=4)

        print(f"Drying process completed on {self.id}")
