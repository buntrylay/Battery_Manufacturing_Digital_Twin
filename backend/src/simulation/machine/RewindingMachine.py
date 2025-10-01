from simulation.machine.BaseMachine import BaseMachine
from dataclasses import dataclass
from simulation.process_parameters.Parameters import RewindingParameters
from simulation.battery_model.RewindingModel import RewindingModel
from simulation.battery_model import ElectrodeInspectionModel


class RewindingMachine(BaseMachine):
    def __init__(
        self,
        process_name: str,
        rewinding_parameters: RewindingParameters,
        rewinding_model: RewindingModel = None,
        connection_string=None,
    ):
        super().__init__(
            process_name,
            rewinding_model,
            rewinding_parameters,
        )

    def receive_model_from_previous_process(
        self,
        assembled_rewinding_model: RewindingModel,
    ):
        self.battery_model = assembled_rewinding_model

    def run(self, end_time=120, step=5):
        self.turn_on()
        all_results = []

        for t in range(0, end_time + 1, step):
            self.total_time = t
            self.battery_model.update_properties(self.machine_parameters)
            result = self.get_current_state()
            all_results.append(result)
            self.save_data_to_local_folder()
        self.save_all_results(all_results)
        self.turn_off()

    def validate_parameters(self, parameters: dict):
        return RewindingParameters(**parameters).validate_parameters()
