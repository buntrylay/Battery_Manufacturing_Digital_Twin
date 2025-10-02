from simulation.machine.BaseMachine import BaseMachine
from dataclasses import dataclass
from simulation.process_parameters.Parameters import ElectrolyteFillingParameters
from simulation.battery_model.RewindingModel import RewindingModel
from simulation.battery_model.ElectrolyteFillingModel import ElectrolyteFillingModel


class ElectrolyteFillingMachine(BaseMachine):
    def __init__(
        self,
        process_name: str,
        electrolyte_filling_parameters: ElectrolyteFillingParameters,
        electrolyte_filling_model: ElectrolyteFillingModel = None,
        connection_string=None,
    ):
        super().__init__(
            process_name, electrolyte_filling_model, electrolyte_filling_parameters
        )

    def receive_model_from_previous_process(self, previous_model: RewindingModel):
        self.battery_model = ElectrolyteFillingModel(previous_model)

    def calculate_total_steps(self):
        if self.battery_model is not None and self.machine_parameters is not None:
            self.total_steps = int(self.machine_parameters.Soaking_time)

    def run(self):
        self.turn_on()
        # the range can be adjusted based on real process time
        for t in range(self.machine_parameters.Soaking_time):
            self.total_time = t
            self.battery_model.update_properties(self.machine_parameters, t)
        self.turn_off()

    def validate_parameters(self, parameters: dict):
        return ElectrolyteFillingParameters(**parameters).validate_parameters()
