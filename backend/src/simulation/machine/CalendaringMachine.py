from simulation.machine.BaseMachine import BaseMachine
from simulation.process_parameters.Parameters import CalendaringParameters
from simulation.battery_model.DryingModel import DryingModel
from simulation.battery_model.CalendaringModel import CalendaringModel


class CalendaringMachine(BaseMachine):
    def __init__(
        self,
        process_name: str,
        calendaring_parameters: CalendaringParameters,
        calendaring_model: CalendaringModel = None,
        connection_string=None,
    ):
        super().__init__(process_name, calendaring_model, calendaring_parameters)

    def receive_model_from_previous_process(self, previous_model: DryingModel):
        self.battery_model = CalendaringModel(
            drying_model=previous_model,
            initial_porosity=self.machine_parameters.initial_porosity,
        )

    def run(self):
        self.turn_on()
        all_results = []

        for t in range(60):
            self.total_time = t
            self.battery_model.update_properties(self.machine_parameters)
            proc = self.battery_model.get_properties()
            result = self.get_current_state(process_specifics=proc)
            all_results.append(result)
            self.save_data_to_local_folder()

        self.save_all_results(all_results)
        self.turn_off()

    def validate_parameters(self, parameters: dict):
        return CalendaringParameters(**parameters).validate_parameters()
