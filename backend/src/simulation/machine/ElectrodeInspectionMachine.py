from dataclasses import dataclass
from simulation.machine.BaseMachine import BaseMachine
from simulation.process_parameters.Parameters import ElectrodeInspectionParameters
from simulation.battery_model.ElectrodeInspectionModel import ElectrodeInspectionModel
from simulation.battery_model.SlittingModel import SlittingModel


class ElectrodeInspectionMachine(BaseMachine):
    def __init__(
        self,
        process_name: str,
        electrode_inspection_parameters: ElectrodeInspectionParameters,
        electrode_inspection_model: ElectrodeInspectionModel = None,
        connection_string=None,
    ):
        super().__init__(
            process_name, electrode_inspection_model, electrode_inspection_parameters
        )

    def receive_model_from_previous_process(self, previous_model: SlittingModel):
        self.battery_model = ElectrodeInspectionModel(previous_model)

    def run(self):
        self.turn_on()
        all_results = []

        # the range can be adjusted based on real process time
        for t in range(10):
            self.total_time = t
            self.battery_model.update_properties(self.machine_parameters)
            result = self.get_current_state()
            all_results.append(result)
            self.save_data_to_local_folder()
        self.save_all_results(all_results)
        self.turn_off()

    def validate_parameters(self, parameters: dict):
        return ElectrodeInspectionParameters(**parameters).validate_parameters()
