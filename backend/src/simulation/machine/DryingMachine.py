from dataclasses import dataclass
from simulation.battery_model import CoatingModel
from simulation.battery_model import DryingModel
from simulation.machine.BaseMachine import BaseMachine
from simulation.process_parameters.Parameters import DryingParameters


class DryingMachine(BaseMachine):
    def __init__(
        self,
        process_name: str,
        drying_model: DryingModel,
        drying_parameters: DryingParameters,
    ):
        super().__init__(process_name, drying_model, drying_parameters)

    def receive_model_from_previous_process(self, previous_model: CoatingModel):
        self.battery_model = DryingModel(previous_model)

    def __init__(self, drying_model, drying_parameters: DryingParameters):
        super().__init__("Drying", drying_model, drying_parameters)

    def run(self):
        self.turn_on()
        all_results = []
        total_steps = self.battery_model.time_steps(
            self.machine_parameters.drying_length, self.machine_parameters.web_speed
        )
        for t in range(total_steps):
            self.total_time = t
            proc = self.battery_model.update_properties(self.machine_parameters)
            result = self.get_current_state(process_specifics=proc)
            all_results.append(result)
            self.save_data_to_local_folder()
        self.save_all_results(all_results)
        self.turn_off()
