from simulation.battery_model import MixingModel, CoatingModel
from simulation.machine.BaseMachine import BaseMachine
from simulation.process_parameters.Parameters import CoatingParameters
import time

# Import notification functions
try:
    # Try multiple import paths to handle different environments
    try:
        from server.notification_queue import notify_machine_status
    except ImportError:
        from backend.src.server.notification_queue import notify_machine_status
except ImportError:
    # Fallback if import fails
    def notify_machine_status(*args, **kwargs):
        print(f"CoatingMachine Notification: {args}")
        pass


def calculate_shear_rate(coating_speed, gap_height):
    """
    Calculate the shear rate in the coating gap.

    The shear rate is a fundamental parameter that affects coating quality and uniformity.
    It is calculated as the ratio of coating speed to gap height.

    Args:
        coating_speed (float): Speed of the coating process in mm/s
        gap_height (float): Height of the coating gap in m

    Returns:
        float: Shear rate in 1/s
    """
    return coating_speed / gap_height


def calculate_uniformity_std(shear_rate):
    """
    Calculate coating uniformity based on shear rate.

    The uniformity is expressed as a standard deviation relative to the nominal
    shear rate. Lower values indicate better coating uniformity.

    Args:
        shear_rate (float): Calculated shear rate in 1/s

    Returns:
        float: Standard deviation of coating uniformity
    """
    base_std = 0.01  # 1%
    nominal_shear_rate = 500  # 1/s
    return base_std * (shear_rate / nominal_shear_rate)


class CoatingMachine(BaseMachine):
    """
    A coating machine that simulates the electrode coating process.

    This class handles the coating process for battery electrodes, including:
    - Multiple coating steps
    - Process parameter simulation
    - Quality metrics calculation
    - Real-time data logging
    """

    def __init__(
        self,
        process_name: str,
        coating_parameters: CoatingParameters,
        coating_model: CoatingModel = None,
        connection_string=None,
    ):
        """
        Initialise the coating machine.

        Args:

        """
        self.shear_rate = 0
        self.uniformity_std = 0
        super().__init__(
            process_name,
            coating_model,
            coating_parameters,
            connection_string,
        )

    def receive_model_from_previous_process(self, previous_model: MixingModel):
        self.battery_model = CoatingModel(previous_model)

    def __simulate(self, duration_sec=100, results_list=None):
        """
        Simulate a single coating step with process parameters and quality metrics.

        Args:
            step (int): Current step number
        """
        last_saved_time = time.time()
        last_saved_result = None
        for t in range(0, duration_sec + 1, 5):
            self.total_time = t
            # update shear rate and wet thickness first to trigger changes in other properties
            self.shear_rate = calculate_shear_rate(
                self.machine_parameters.coating_speed,
                self.machine_parameters.gap_height,
            )
            self.uniformity_std = calculate_uniformity_std(self.shear_rate)
            # Update model using the full parameters object
            self.battery_model.update_properties(self.machine_parameters)
            self.battery_model.shear_rate = self.shear_rate
            self.battery_model.uniformity = 1 - self.uniformity_std
            self.battery_model.temperature = 25.0
            result = self.get_current_state(
                process_specifics={
                    "shear_rate": self.shear_rate,
                    "uniformity_std": self.uniformity_std,
                }
            )
            results_list.append(result)
            # Save results periodically, but only if data has changed
            now = time.time()
            if (
                now - last_saved_time >= 0.1 and result != last_saved_result
            ):  # Check if data has changed
                # self.send_json_to_iothub(result)  # Send to IoT Hub
                self.save_data_to_local_folder()  # Print to console
                last_saved_time = now
                last_saved_result = result
            time.sleep(0.1)

    def run(self):
        """
        Run the coating process with detailed step simulation.
        """
        self.turn_on()
        
        # Notify start of coating process
        notify_machine_status(
            machine_id=self.process_name,
            line_type=self.process_name.split('_')[-1],
            process_name=self.process_name,
            status="coating_started",
            data={
                "message": f"Starting {self.process_name} coating process",
                "coating_speed": self.machine_parameters.coating_speed,
                "gap_height": self.machine_parameters.gap_height,
                "flow_rate": self.machine_parameters.flow_rate,
                "coating_width": self.machine_parameters.coating_width
            }
        )
        
        all_results = []
        self.__simulate(results_list=all_results)
        self.save_all_results(all_results)
        
        # Notify completion
        notify_machine_status(
            machine_id=self.process_name,
            line_type=self.process_name.split('_')[-1],
            process_name=self.process_name,
            status="coating_completed",
            data={
                "message": f"{self.process_name} coating completed successfully",
                "total_results": len(all_results),
                "final_shear_rate": getattr(self, 'shear_rate', 0),
                "final_uniformity_std": getattr(self, 'uniformity_std', 0),
                "final_state": self.get_current_state()
            }
        )
        
        self.turn_off()

    def validate_parameters(self, parameters: dict):
        return CoatingParameters(**parameters).validate_parameters()
