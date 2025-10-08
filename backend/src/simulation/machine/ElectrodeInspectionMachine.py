import random
from simulation.machine.BaseMachine import BaseMachine
from simulation.process_parameters.Parameters import ElectrodeInspectionParameters
from simulation.battery_model.ElectrodeInspectionModel import ElectrodeInspectionModel
from simulation.battery_model.SlittingModel import SlittingModel
from simulation.event_bus.events import EventBus


class ElectrodeInspectionMachine(BaseMachine):
    def __init__(
        self,
        process_name: str,
        electrode_inspection_parameters: ElectrodeInspectionParameters,
        electrode_inspection_model: ElectrodeInspectionModel = None,
        event_bus: EventBus = None,
    ):
        super().__init__(
            process_name,
            electrode_inspection_model,
            electrode_inspection_parameters,
            event_bus,
        )

    def calculate_total_steps(self):
        self.total_steps = 10

    def receive_model_from_previous_process(self, previous_model: SlittingModel):
        self.battery_model = ElectrodeInspectionModel(previous_model)

    def step_logic(self, t: int, verbose: bool):
        pass

    def validate_parameters(self, parameters):
        if isinstance(parameters, ElectrodeInspectionParameters):
            return parameters.validate_parameters()
        elif isinstance(parameters, dict):
            return ElectrodeInspectionParameters(**parameters).validate_parameters()
        else:
            raise TypeError(f"Expected ElectrodeInspectionParameters or dict, got {type(parameters)}")
