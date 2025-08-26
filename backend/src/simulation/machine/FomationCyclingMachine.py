import os
import json
import time
import threading
from datetime import datetime, timedelta
import numpy as np # For np.exp if not used directly in calculator
from simulation.machine.BaseMachine import BaseMachine
from simulation.sensor.FormationCyclingCalculation import FormationCyclingCalculation # Ensure this path is correct
from metrics.metrics import set_machine_status
class FormationCyclingMachine(BaseMachine):

    """

    Simulates the initial formation cycle (charging) of a battery cell.

    Focuses on SEI layer formation and initial capacity/voltage response.

    """
 
    def __init__(self, id: str, machine_parameters: dict):
        super().__init__(id)
        self.name = "FormationCyclingMachine"
       
        self.start_datetime = datetime.now()
        self.total_simulation_time_s = 0
        self.lock = threading.Lock()
        self.is_on = True
 
        self.output_dir = os.path.join(os.getcwd(), "formation_cycling_output")
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory for {self.id} created at: {self.output_dir}")
 
        # --- Parameters from machine_parameters ---

        self.I_charge_A = machine_parameters.get("Charge_current_A")
        self.V_charge_max_V = machine_parameters.get("Charge_voltage_limit_V")
        self.V0_cell_V = machine_parameters.get("Voltage") # Initial voltage for the cycle

        # Model parameters for the calculator
        self.Q_theoretical_Ah = 2
        self.k_sei = 0.05
        self.t50 = 300

        # Total duration for this simplified first charge cycle simulation

        self.formation_duration_s = machine_parameters.get("Formation_duration_s", 200)
 
 
        self.calculator = FormationCyclingCalculation()
 
        # --- Inputs from Previous Process (Electrolyte Filling) ---

        self.initial_electrolyte_volume_cm3 = None
        self.initial_wetting_efficiency = None

        # Defect flags from prior steps could be added here if needed to influence V0 or Q_theoretical
 
        # --- Simulation State Variables ---

        self.current_voltage_V = self.V0_cell_V
        self.sei_efficiency = 0.0
        self.cell_capacity_Ah = 0.0
        self.final_properties_summary = {}
 
    def update_from_filling(self, filling_data: dict):
        with self.lock:
            self.initial_electrolyte_volume_cm3 = filling_data.get("volume_electrolyte")
            self.initial_wetting_efficiency = filling_data.get("wetting_efficiency")
            print(f"[{self.id}] Received from Electrolyte Filling: "
                  f"Volume={self.initial_electrolyte_volume_cm3} cm³, WettingEff={self.initial_wetting_efficiency}")

            # Reset voltage to V0 for the cycle based on filled cell state
            self.current_voltage_V = self.V0_cell_V # Or adjust V0 based on filling_data if model supports
 
    def _format_result(self, is_final=False):

        with self.lock:

            timestamp = (self.start_datetime + timedelta(seconds=self.total_simulation_time_s)).isoformat()
            base = {
                "TimeStamp": timestamp,
                "Duration_s": round(self.total_simulation_time_s, 2),
                "Machine_ID": self.id,
                "Process": "Formation_Cycling_FirstCharge"
            }

            properties = {
                "Voltage_V": round(self.current_voltage_V, 4),
                "Current_A": round(self.I_charge_A, 3), # Assuming only charging in this simplified model
                "SEI_Efficiency": round(self.sei_efficiency, 4),
                "Cell_Capacity_Ah": round(self.cell_capacity_Ah, 4),
            }
            if is_final:
                base["Final Properties"] = properties
            else:
                base.update(properties)
            return base
 
    def _write_json(self, data, filename_suffix):
        try:
            timestamp_str = data["TimeStamp"].replace(":", "-").replace(".", "-")
            unique_filename = os.path.join(self.output_dir, f"{self.id}_{timestamp_str}_{filename_suffix}.json")
            with open(unique_filename, 'w') as f:
                json.dump(data, f, indent=4)
            # print(f"Data written to {unique_filename}") # Potentially too verbose for many steps
        except Exception as e:

            print(f"Error writing JSON for {self.id}: {e}")
 
    def _simulate(self, delta_t_s=1):

        print(f"[{self.id}] Starting Simplified Formation Cycling (First Charge) for {self.formation_duration_s}s.")
        num_steps = int(self.formation_duration_s / delta_t_s)
        last_saved_time = time.time()
        last_saved_result = None
 
        for i in range(num_steps + 1):
            t = i * delta_t_s
            self.total_simulation_time_s = t
            self.sei_efficiency = self.calculator.calculate_sei_efficiency(self.k_sei, self.t50, t)
            self.cell_capacity_Ah = self.calculator.calculate_cell_capacity_ah(self.sei_efficiency, self.Q_theoretical_Ah)
            # Calculate voltage based on the time into this charge phase
            # V0 for this calculation is the initial voltage of the cell at the start of formation.
            self.current_voltage_V = self.calculator.calculate_voltage_charge_cc(
                self.V0_cell_V, self.I_charge_A, t, self.cell_capacity_Ah
            )

            if self.current_voltage_V >= self.V_charge_max_V:
                self.current_voltage_V = self.V_charge_max_V # Cap voltage
                # Log this step and then potentially break or stop further changes
                result = self._format_result()
                self._write_json(result, f"charge_t{round(self.total_simulation_time_s)}s_VOLTAGE_LIMIT_REACHED")
                print(f"[{self.id}] Voltage limit reached at {self.total_simulation_time_s}s.")
                break # End simulation for this charge once max voltage is hit
 
            result = self._format_result()
            now = time.time()

            if now - last_saved_time >= 0.05: # Log more frequently if desired, or based on change
                if result != last_saved_result:
                    self._write_json(result, f"charge_t{round(self.total_simulation_time_s)}s")
                    last_saved_result = result
                last_saved_time = now

            time.sleep(0.001) # Minimal sleep for simulation speed
        self._write_json(self._format_result(is_final=True), f"FINAL_summary_first_charge")

        print(f"[{self.id}] Simplified Formation First Charge completed.")
 
    def run(self):

        if self.is_on:
            set_machine_status(self.id, 1)
            try:

                # Ensure inputs from previous stage are available if needed
                if self.initial_wetting_efficiency is None: # Example check
                    print(f"Warning: [{self.id}] Inputs from electrolyte filling not updated. Using defaults/initials.")
                self._simulate()
                print(f"Formation cycling process completed on {self.id}\n")
                set_machine_status(self.id, 0)  # <-- ADDED: Set status to
            except Exception as e:
                print(f"Error during formation cycling on {self.id}: {e}")
                set_machine_status(self.id, 2)  # <-- ADDED: Set status to 2 (Fault)
            
 
    def get_final_formation_properties(self):
        with self.lock:
            # For this simplified version, we return the state after the first charge attempt
            return {
                "machine_id": self.id,
                # "electrode_type": self.electrode_type,
                "final_simulated_duration_s": self.total_simulation_time_s,
                "final_voltage_V": self.current_voltage_V,
                "final_sei_efficiency": self.sei_efficiency,
                "final_cell_capacity_Ah": self.cell_capacity_Ah,
                **self.final_properties_summary # Add all properties from the final step
            }
 