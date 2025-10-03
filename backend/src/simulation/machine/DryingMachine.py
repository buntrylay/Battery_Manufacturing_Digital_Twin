from dataclasses import dataclass
from simulation.battery_model import CoatingModel
from simulation.battery_model.DryingModel import DryingModel
from simulation.machine.BaseMachine import BaseMachine
from simulation.process_parameters.Parameters import DryingParameters


class DryingMachine(BaseMachine):
    def __init__(
        self,
        process_name: str,
        drying_parameters: DryingParameters,
        drying_model: DryingModel = None,
        connection_string=None,
    ):
        super().__init__(process_name, drying_model, drying_parameters)

    def receive_model_from_previous_process(self, previous_model: CoatingModel):
        self.battery_model = DryingModel(previous_model)
    
    # def step_logic(self, t: int):
    #     pass

    def calculate_total_steps(self):
        if self.battery_model is not None and self.machine_parameters is not None:
            DELTA_T = 1
            residence_time = self.battery_model.drying_length / self.machine_parameters.web_speed
            self.total_steps = int(residence_time / DELTA_T)

    def run(self):
        self.turn_on()
        total_steps = self.battery_model.time_steps(self.machine_parameters.web_speed)
        for t in range(total_steps):
            self.total_time = t
            self.battery_model.update_properties(self.machine_parameters)
        self.turn_off()

    def step_logic(self, tick):
        """
        Update the properties of the drying model.
        """
        pass

    def validate_parameters(self, parameters: dict):
        return DryingParameters(**parameters).validate_parameters()
