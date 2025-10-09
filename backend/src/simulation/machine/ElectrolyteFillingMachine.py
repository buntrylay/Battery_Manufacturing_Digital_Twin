from simulation.event_bus.events import EventBus
from simulation.machine.BaseMachine import BaseMachine
from simulation.process_parameters.Parameters import ElectrolyteFillingParameters
from simulation.battery_model.RewindingModel import RewindingModel
from simulation.battery_model.ElectrolyteFillingModel import ElectrolyteFillingModel


class ElectrolyteFillingMachine(BaseMachine):
    def __init__(
        self,
        process_name: str,
        electrolyte_filling_parameters: ElectrolyteFillingParameters,
        electrolyte_filling_model: ElectrolyteFillingModel = None,
        event_bus: EventBus = None,
    ):
        super().__init__(
            process_name,
            electrolyte_filling_model,
            electrolyte_filling_parameters,
            event_bus,
        )

    def receive_model_from_previous_process(self, previous_model: RewindingModel):
        self.battery_model = ElectrolyteFillingModel(previous_model)

    def calculate_total_steps(self):
        self.total_steps = int(self.machine_parameters.soaking_time)

    def step_logic(self, t: int, verbose: bool):
        pass

    def validate_parameters(self, parameters: dict):
        return ElectrolyteFillingParameters(**parameters).validate_parameters()
