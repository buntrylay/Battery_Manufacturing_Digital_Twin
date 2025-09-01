import os
import json
import time
import threading
from datetime import datetime, timedelta
from simulation.machine.BaseMachine import BaseMachine
from simulation.sensor.RewindingPropertyCalculator import RewindingPropertyCalculator
from metrics.metrics import set_machine_status
class RewindingMachine(BaseMachine):
    """
    A rewinding machine that simulates the electrode rewinding process.
    
    This class handles the rewinding process for battery electrodes, including:
    - Rewinding parameters simulation
    - Quality metrics calculation
    - Real-time data logging
    """
    
    def __init__(self, id, machine_parameters: dict):
        """
        Initialize the rewinding machine.
        
        Args:
            id (str): Unique identifier for the machine
        """
        super().__init__(id)
        self.start_datetime = datetime.now()
        self.total_time = 0
        self.lock = threading.Lock()

        # Create output directory
        self.output_dir = os.path.join(os.getcwd(), "rewinding_output")
        os.makedirs(self.output_dir, exist_ok=True)
        print(f"Output directory created at: {self.output_dir}")
        
        # Initialise calculator and process parameters
        self.calculator = RewindingPropertyCalculator()
        
        # Input parameters
        self.tau_initial = machine_parameters["initial_tension"]  # N
        self.n_taper = machine_parameters["tapering_steps"]  # Number of tapering steps
        self.v_rewind = machine_parameters["rewinding_speed"]  # m/s
        self.H_env = machine_parameters["environment_humidity"]  # Relative humidity (0-1)
        self.L_wound = 0
        # Variables from previous processes
        self.delta_cal = None
        self.phi_final = None

    def update_from_inspection(self, inspection_data):
        """
        Update the machine parameters based on electrode inspection data.
        
        Args:
            inspection_data (dict): Data from the electrode inspection process.
        """
        with self.lock:
            self.delta_cal = inspection_data.get("delta_el")
            self.phi_final = inspection_data.get("phi_final")
            self.final_width = inspection_data.get("final_width")
            self.final_thickness_m = inspection_data.get("final_thickness_m")
            self.epsilon_width = inspection_data.get("epslon_width")
            print(f"{self.id}: Received from electrode inspection - delta_cal={self.delta_cal}")
            

    def _format_result(self, step=None, is_final=False):
        with self.lock:
            base = {
                "TimeStamp": (self.start_datetime + timedelta(seconds=self.total_time)).isoformat(),
                "Duration": round(self.total_time, 5),
                "Machine ID": self.id,
                "Process": "Rewinding"
            }

            properties = {
                "Enviromental Control": self.H_env,
                "Wound length": round(self.L_wound,8),
                "Roll diameter": round(self.D_roll, 8),
                "Roll hardness": round(self.H_roll, 8),
                "Web tension": round(self.tau_rewind, 8)
            }

            if is_final:
                base["Final Properties"] = properties
            else:
                base.update(properties)

            return base

    def _write_json(self, data, filename):
        """
        Write the formatted data to a JSON file.
        
        Args:
            data (dict): Data to write.
            filename (str): Name of the file to write to.
        """
        try:
            timestamp = data["TimeStamp"].replace(":", "-").replace(".", "-")
            unique_filename = f"rewinding_output/{self.id}_{timestamp}_{filename}"
            
            with open(unique_filename, 'w') as f:
                json.dump(data, f, indent=4)
            print(f"Data written to {unique_filename}")
        except Exception as e:
            print(f"Error writing JSON: {e}")

    def _simulate(self, end_time=120):
        last_saved_time = time.time()
        last_saved_result = None
        
        for t in range(0, end_time + 1, 5):
            self.total_time = t
            # Update parameters based on the current time
            self.L_wound += self.v_rewind * t
            self.D_roll = self.calculator.D_roll(self.L_wound, self.delta_cal)
            self.tau_rewind = self.calculator.tau_rewind(self.D_roll, self.tau_initial, self.n_taper)
            self.H_roll = self.calculator.H_roll(self.delta_cal, self.tau_rewind)

            # Format and write the result
            result = self._format_result()
            
            now = time.time()
            if now - last_saved_time >= 0.1 and result != last_saved_result:  # Check if data has changed
                filename = f"result_at_{round(self.total_time)}s.json"
                self._write_json(result, filename)
                last_saved_time = now
                last_saved_result = result
            
            time.sleep(0.1)
                
    def run(self):
        if self.state:
            self._simulate()
            from server.main import thread_broadcast
            thread_broadcast(f"Rewinding process {self.id} in progress...") # Broadcast continuation message
            final_output = self._format_result(is_final=True)
            filename = f"final_results_{self.id}.json"
            self._write_json(final_output, filename)
            print(f"Rewinding process completed on {self.id}\n")
            thread_broadcast(f"Rewinding process {self.id} completed") # Broadcast completion message
            print(f"Rewinding process completed on {self.id}\n")
    
    def get_final_rewind(self):
        return {
            "phi_final" : self.phi_final,
            "wound_length": self.L_wound,
            "epsilon_width": self.epsilon_width,
            "final_width": self.final_width,
            "final_thickness_m": self.final_thickness_m
            
        }
            
    