from simulation.machine.BaseMachine import BaseMachine
from dataclasses import dataclass
from simulation.process_parameters.Parameters import SlittingParameters
from simulation.battery_model import CalendaringModel
from simulation.battery_model.SlittingModel import SlittingModel


class SlittingMachine(BaseMachine):
    def __init__(
        self,
        process_name: str,
        slitting_parameters: SlittingParameters,
        slitting_model: SlittingModel = None,
        connection_string=None,
    ):
        super().__init__(
            process_name, slitting_model, slitting_parameters, connection_string
        )
        # self.total_steps = 30

    def receive_model_from_previous_process(self, previous_model: CalendaringModel):
        self.battery_model = SlittingModel(previous_model)

    def calculate_total_steps(self):
        self.total_steps = 10  # default

    def step_logic(self, t: int):
        pass

    def validate_parameters(self, parameters: dict):
        return SlittingParameters(**parameters).validate_parameters()
