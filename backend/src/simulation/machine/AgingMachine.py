import simulation.machine.BaseMachine as BaseMachine
from dataclasses import dataclass
from simulation.process_parameters.Parameters import AgingParameters
from simulation.battery_model.AgingModel import AgingModel
from simulation.battery_model.FormationCyclingModel import FormationCyclingModel


class AgingMachine(BaseMachine):

    def __init__(
        self,
        process_name: str,
        aging_parameters: AgingParameters,
        aging_model: AgingModel = None,
        connection_string=None,
    ):
        super().__init__(process_name, aging_model, aging_parameters)

    def receive_model_from_previous_process(
        self, previous_model: FormationCyclingModel
    ):
        self.battery_model = AgingModel(previous_model)

    def run(self):
        self.turn_on()
        all_results = []
        # the range can be adjusted based on real process time
        for t in range(
            0, int(self.machine_parameters.aging_time_days * 24 * 3600) + 1, 3600
        ):
            self.total_time = t
            self.battery_model.update_properties(self.machine_parameters, t)
            result = self.get_current_state()
            all_results.append(result)
            self.save_data_to_local_folder()
        self.save_all_results(all_results)
        self.turn_off()

    def validate_parameters(self, parameters: dict):
        return AgingParameters(**parameters).validate_parameters()
