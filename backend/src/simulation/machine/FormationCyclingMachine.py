from simulation.event_bus.events import EventBus
from simulation.machine.BaseMachine import BaseMachine
from simulation.process_parameters.Parameters import FormationCyclingParameters
from simulation.battery_model.FormationCyclingModel import FormationCyclingModel
from simulation.battery_model.ElectrolyteFillingModel import ElectrolyteFillingModel


class FormationCyclingMachine(BaseMachine):
    def __init__(
        self,
        process_name: str,
        formation_cycling_parameters: FormationCyclingParameters,
        formation_model: FormationCyclingModel = None,
        event_bus: EventBus = None,
    ):
        super().__init__(
            process_name, formation_model, formation_cycling_parameters, event_bus
        )

    def receive_model_from_previous_process(
        self, previous_model: ElectrolyteFillingModel
    ):
        self.battery_model = FormationCyclingModel(previous_model)

    def calculate_total_steps(self):
        self.total_steps = int(self.machine_parameters.formation_duration_s + 1)

    def step_logic(self, t: int, verbose: bool):
        if self.battery_model.voltage >= self.machine_parameters.charge_voltage_limit_V:
            if verbose: 
                print(f"{self.process_name}: Voltage limit reached at step {t}")
            raise RuntimeError("Voltage limit was reached")

    def validate_parameters(self, parameters: dict):
        return FormationCyclingParameters(**parameters).validate_parameters()
