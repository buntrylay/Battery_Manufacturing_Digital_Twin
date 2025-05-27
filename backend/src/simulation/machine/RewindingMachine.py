import os
import json
import time
import threading
from datetime import datetime, timedelta
from simulation.machine.BaseMachine import BaseMachine
from simulation.sensor.RewindingPropertyCalculator import RewindingPropertyCalculator

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
        
        # Variables from previous processes
        self.delta_cal = None


    def update_from_inspection(self, inspection_data: dict):
        """
        Update the machine parameters based on electrode inspection data.
        
        Args:
            inspection_data (dict): Data from the electrode inspection process.
        """
        with self.lock:
            self.delta_cal = inspection_data.get("delta_cal", None)
            print(f"{self.id}: Received from electrode inspection - delta_cal={self.delta_cal}")
            
            self.L_wound = self.calculator.L_wound(self.delta_cal, self.n_taper)
            self.D_roll = self.calculator.d_roll(self.delta_cal, self.n_taper)
            self.H_roll = self.calculator.H_roll(self.delta_cal, self.n_taper)
            self.tau_rewind = self.calculator.tau_rewind(self.D_roll, self.tau_initial, self.n_taper)

    def _format_result(self, end_time=120, step=1):

        """
        Format the result for output.
        """
        with self.lock:
            result = {
                "TimeStamp": (self.start_datetime + timedelta(seconds=self.total_time)).isoformat(),
                "Duration": round(self.total_time, 5),
                "Machine ID": self.id,
                "Process": "Rewinding",
                "L_wound": round(self.L_wound, 4),
                "D_roll": round(self.D_roll, 4),
                "H_roll": round(self.H_roll, 4),
                "tau_rewind": round(self.tau_rewind, 4),
                "delta_cal": round(self.delta_cal, 4)
            }

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

    def _simulate(self, end_time=120, interval=1):
        """
        Simulate the rewinding process.
        
        Args:
            end_time (int): Total simulation time in seconds.
            interval (int): Time interval for each simulation step.
        """
        last_saved_time = time.time()
        last_saved_result = None

        for t in range(0, end_time + 1, interval):
            self.total_time = t
            
            # Update parameters based on the current time
            self.tau_rewind = self.calculator.tau_rewind(self.D_roll, self.tau_initial, self.n_taper)
            self.L_wound = self.calculator.L_wound(self.delta_cal, self.n_taper)
            self.D_roll = self.calculator.d_roll(self.delta_cal, self.n_taper)
            self.H_roll = self.calculator.H_roll(self.delta_cal, self.n_taper)

            # Format and write the result
            result = self._format_result(end_time=end_time, step=t)
            if time.time() - last_saved_time >= 5 or t == end_time:
                if last_saved_result != result:
                    self._write_json(result, f"rewinding_step_{t}.json")
                    last_saved_result = result
                    last_saved_time = time.time()
                    
                time.sleep(0.1)  # Simulate real-time processing
                
    def run(self):
        if self.is_on:
            self._simulate()
            
            final_output = self._format_result(end_time=120, step=120)
            filename = f"final_results_{self.id}.json"
            self._write_json(final_output, filename)
            print(f"Rewinding process completed on {self.id}\n")
