from simulation.battery_model import MixingModel, CoatingModel
from simulation.machine.BaseMachine import BaseMachine
from simulation.process_parameters.Parameters import CoatingParameters
from simulation.event_bus.events import EventBus


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
        event_bus: EventBus = None,
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
            event_bus,
        )

    def receive_model_from_previous_process(self, previous_model: MixingModel):
        self.battery_model = CoatingModel(previous_model)

    def calculate_total_steps(self):
        self.total_steps = 20  # b/c originally, there is duration_secs = 100 and time steps = 5

    def step_logic(self, t: int, verbose: bool):
        # update shear rate and wet thickness first to trigger changes in other properties
        self.shear_rate = calculate_shear_rate(
            self.machine_parameters.coating_speed,
            self.machine_parameters.gap_height,
        )
        self.uniformity_std = calculate_uniformity_std(self.shear_rate)
        self.append_process_specifics(
            {
                "shear_rate": self.shear_rate,
                "uniformity_std": self.uniformity_std,
            }
        )

    def validate_parameters(self, parameters: dict):
        return CoatingParameters(**parameters).validate_parameters()
