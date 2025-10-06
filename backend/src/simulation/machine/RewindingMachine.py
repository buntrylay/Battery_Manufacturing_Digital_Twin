from simulation.event_bus.events import EventBus
from simulation.machine.BaseMachine import BaseMachine
from simulation.process_parameters.Parameters import RewindingParameters
from simulation.battery_model.RewindingModel import RewindingModel


class RewindingMachine(BaseMachine):
    def __init__(
        self,
        process_name: str,
        rewinding_parameters: RewindingParameters,
        rewinding_model: RewindingModel = None,
        event_bus: EventBus = None,
    ):
        super().__init__(process_name, rewinding_model, rewinding_parameters, event_bus)
        # self.total_steps = 120 // 5

    def receive_model_from_previous_process(
        self,
        assembled_rewinding_model: RewindingModel,
    ):
        self.battery_model = assembled_rewinding_model

    def calculate_total_steps(self):
        self.total_steps = 10

    def step_logic(self, t: int, verbose: bool):
        pass

    def validate_parameters(self, parameters: dict):
        return RewindingParameters(**parameters).validate_parameters()
