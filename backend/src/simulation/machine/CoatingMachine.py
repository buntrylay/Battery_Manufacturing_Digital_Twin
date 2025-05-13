from simulation.machine.BaseMachine import BaseMachine
import time
from datetime import datetime, timedelta
import json
import os

class CoatingMachine(BaseMachine):
    """
    A coating machine that simulates the electrode coating process.
    """
    
    def __init__(self, id):
        """
        Initialize the coating machine.
        
        Args:
            id (str): Unique identifier for the machine
        """
        super().__init__(id)
        self.steps = 3  # Number of coating steps
        self.start_datetime = datetime.now()
        self.total_time = 0
        self.output_dir = os.path.join(os.getcwd(), "simulation_output")
        os.makedirs(self.output_dir, exist_ok=True)

    def _format_result(self, step=None, is_final=False):
        """
        Format the current or final process data as a dictionary.
        """
        base = {
            "TimeStamp": (self.start_datetime + timedelta(seconds=self.total_time)).isoformat(),
            "Duration": round(self.total_time, 5),
            "Machine ID": self.id,
            "Process": "Coating",
            "Step": step if step else "Final"
        }
        
        if is_final:
            base["Status"] = "Completed"
            base["Total Steps"] = self.steps
        else:
            base["Status"] = "In Progress"
            base["Current Step"] = step
            base["Remaining Steps"] = self.steps - step

        return base

    def _write_json(self, data, filename):
        """
        Write a dictionary to a JSON file.
        """
        try:
            timestamp = data["TimeStamp"].replace(":", "-").replace(".", "-")
            unique_filename = f"simulation_output/{self.id}_{timestamp}_{filename}"
            
            with open(unique_filename, "w") as f:
                json.dump(data, f, indent=4)
            print(f"Results saved to {unique_filename}")
        except Exception as e:
            print(f"Error writing result to file: {e}")

    def run(self):
        """
        Run the coating process with detailed step simulation.
        """
        if self.is_on:
            print(f"\nStarting coating process on {self.id}")
            
            for step in range(1, self.steps + 1):
                print(f"Coating step {step}")
                
                # Simulate coating process
                self.total_time += 5  # 5 seconds per step
                time.sleep(1)  # Simulate time taken for each step
                
                # Record process data
                result = self._format_result(step=step)
                filename = f"result_at_step_{step}.json"
                self._write_json(result, filename)
                
                # Simulate process parameters
                print(f"Step {step} parameters:")
                print(f"- Temperature: {round(25 + step * 2, 1)}°C")
                print(f"- Speed: {100 + step * 20} mm/s")
                print(f"- Thickness: {100 + step * 10} μm")
            
            # Save final results
            final_result = self._format_result(is_final=True)
            filename = f"final_results_{self.id}.json"
            self._write_json(final_result, filename)
            
            print(f"Coating process completed on {self.id}\n") 