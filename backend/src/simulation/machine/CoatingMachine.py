from simulation.battery_model.CoatingModel import CoatingModel
from simulation.machine.BaseMachine import BaseMachine
import time
from dataclasses import dataclass


@dataclass
class CoatingParameters:
    coating_speed: float
    gap_height: float
    flow_rate: float
    coating_width: float
from dataclasses import dataclass


@dataclass
class CoatingParameters:
    coating_speed: float
    gap_height: float
    flow_rate: float
    coating_width: float


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
        coating_model: CoatingModel,
        machine_parameters: CoatingParameters,
        connection_string=None,
    ):

    def __init__(
        self,
        coating_model: CoatingModel,
        machine_parameters: CoatingParameters,
        connection_string=None,
    ):
        """
        Initialise the coating machine.

        Initialise the coating machine.

        Args:

        """
        self.shear_rate = 0
        self.uniformity_std = 0
        super().__init__(
            f"Coating_{coating_model.electrode_type}",
            coating_model,
            machine_parameters,
            connection_string,
        )

    def __calculate_shear_rate(self, coating_speed, gap_height):
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

    def __calculate_uniformity_std(self, shear_rate):
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

        """
        self.shear_rate = 0
        self.uniformity_std = 0
        super().__init__(
            f"Coating_{coating_model.electrode_type}",
            coating_model,
            machine_parameters,
            connection_string,
        )

    def __calculate_shear_rate(self, coating_speed, gap_height):
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

    def __calculate_uniformity_std(self, shear_rate):
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

    def __simulate(self, duration_sec=100, results_list=None):
    def __simulate(self, duration_sec=100, results_list=None):
        """
        Simulate a single coating step with process parameters and quality metrics.


        Args:
            step (int): Current step number
        """
        last_saved_time = time.time()
        last_saved_result = None
        for t in range(0, duration_sec + 1, 5):
        for t in range(0, duration_sec + 1, 5):
            self.total_time = t
            # update shear rate and wet thickness first to trigger changes in other properties
            self.shear_rate = self.__calculate_shear_rate(
                self.machine_parameters.coating_speed, self.machine_parameters.gap_height
            )
            self.uniformity_std = self.__calculate_uniformity_std(self.shear_rate)
            self.battery_model.update_properties(
                self.machine_parameters.flow_rate,
                self.machine_parameters.coating_speed,
                self.machine_parameters.coating_width,
                self.machine_parameters.gap_height,
            )
            result = self.get_current_properties(
                process_specifics={
                    "shear_rate": self.shear_rate,
                    "uniformity_std": self.uniformity_std,
                }
            )
            results_list.append(result)
            # Save results periodically, but only if data has changed
            # update shear rate and wet thickness first to trigger changes in other properties
            self.shear_rate = self.__calculate_shear_rate(
                self.machine_parameters.coating_speed, self.machine_parameters.gap_height
            )
            self.uniformity_std = self.__calculate_uniformity_std(self.shear_rate)
            self.battery_model.update_properties(
                self.machine_parameters.flow_rate,
                self.machine_parameters.coating_speed,
                self.machine_parameters.coating_width,
                self.machine_parameters.gap_height,
            )
            result = self.get_current_properties(
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
        all_results = []
        self.__simulate(results_list=all_results)
        self.save_all_results(all_results)
        self.turn_off()
