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
        self.total_steps = 10

    # def step_logic(self, t: int):
    #     pass

    def receive_model_from_previous_process(self, previous_model: SlittingModel):
        self.battery_model = ElectrodeInspectionModel(previous_model)

    def validate_parameters(self, parameters: dict):
        return ElectrodeInspectionParameters(**parameters).validate_parameters()
