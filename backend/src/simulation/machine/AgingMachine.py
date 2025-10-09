from simulation.machine.BaseMachine import BaseMachine
from simulation.process_parameters.Parameters import AgingParameters
from simulation.battery_model.AgingModel import AgingModel
from simulation.battery_model.FormationCyclingModel import FormationCyclingModel
from simulation.event_bus.events import EventBus


class AgingMachine(BaseMachine):
    def __init__(
        self,
        process_name: str,
        aging_parameters: AgingParameters,
        aging_model: AgingModel = None,
        event_bus: EventBus = None,
    ):
        super().__init__(process_name, aging_model, aging_parameters, event_bus)

    def receive_model_from_previous_process(
        self, previous_model: FormationCyclingModel
    ):
        self.battery_model = AgingModel(previous_model)

    def calculate_total_steps(self):
        self.total_steps = int(self.machine_parameters.aging_time_days * 24)

    def step_logic(self, t: int, verbose: bool):
        seconds_elapsed = t * 3600
        # Start
        if t == 0:
            pass
        # Progress
        if (t % 24 == 0 and t > 0) or (t == self.total_steps - 1):
            days_elapsed = t / 24
            progress = (t / self.total_steps) * 100
        # Completed
        if t == self.total_steps - 1:
            pass

    def validate_parameters(self, parameters: dict):
        return AgingParameters(**parameters).validate_parameters()
