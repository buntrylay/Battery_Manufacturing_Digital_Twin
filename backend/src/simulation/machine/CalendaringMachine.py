from simulation.event_bus.events import EventBus
from simulation.machine.BaseMachine import BaseMachine
from simulation.process_parameters.Parameters import CalendaringParameters
from simulation.battery_model.DryingModel import DryingModel
from simulation.battery_model.CalendaringModel import CalendaringModel


class CalendaringMachine(BaseMachine):
    def __init__(
        self,
        process_name: str,
        calendaring_parameters: CalendaringParameters,
        calendaring_model: CalendaringModel = None,
        event_bus: EventBus = None,
    ):
        super().__init__(
            process_name, calendaring_model, calendaring_parameters, event_bus
        )

    def receive_model_from_previous_process(self, previous_model: DryingModel):
        self.battery_model = CalendaringModel(
            drying_model=previous_model,
            initial_porosity=self.machine_parameters.initial_porosity,
        )

    def calculate_total_steps(self):
        self.total_steps = 60 # placeholder for a fixed number of steps

    def step_logic(self, t: int, verbose: bool):
        pass

    def validate_parameters(self, parameters: dict):
        return CalendaringParameters(**parameters).validate_parameters()
