from simulation.battery_model import CoatingModel, DryingModel
from simulation.machine.BaseMachine import BaseMachine
from simulation.process_parameters.Parameters import DryingParameters
from simulation.event_bus.events import EventBus


class DryingMachine(BaseMachine):
    def __init__(
        self,
        process_name: str,
        drying_parameters: DryingParameters,
        drying_model: DryingModel = None,
        event_bus: EventBus = None,
    ):
        super().__init__(process_name, drying_model, drying_parameters, event_bus)

    def receive_model_from_previous_process(self, previous_model: CoatingModel):
        self.battery_model = DryingModel(previous_model)

    def calculate_total_steps(self):
        DELTA_T = 1
        residence_time = (
            self.battery_model.drying_length / self.machine_parameters.web_speed
        )
        self.total_steps = int(residence_time / DELTA_T)

    def step_logic(self, t: int, verbose: bool):
        self.evap_rate = self.battery_model.evaporation_rate()

    def validate_parameters(self, parameters: dict):
        return DryingParameters(**parameters).validate_parameters()
