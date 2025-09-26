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
        connection_string=None,
    ):
        super().__init__(
            process_name,
            formation_model,
            formation_cycling_parameters,
        )

    def receive_model_from_previous_process(
        self, previous_model: ElectrolyteFillingModel
    ):
        self.battery_model = FormationCyclingModel(previous_model)

    def run(self):
        self.turn_on()
        all_results = []

        for t in range(self.machine_parameters.Formation_duration_s + 1):
            self.total_time = t
            self.battery_model.update_properties(self.machine_parameters, t)
            proc = self.battery_model.get_properties()
            result = self.get_current_state(process_specifics=proc)
            all_results.append(result)
            self.save_data_to_local_folder()

            # stop early if reached voltage limit
            if proc["Voltage_V"] >= self.machine_parameters.Charge_voltage_limit_V:
                break

        self.save_all_results(all_results)
        self.turn_off()

    def validate_parameters(self, parameters: dict):
        return FormationCyclingParameters(**parameters).validate_parameters()
