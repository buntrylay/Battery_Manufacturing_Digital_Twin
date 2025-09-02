from simulation.machine.BaseMachine import BaseMachine
from dataclasses import dataclass

@dataclass
class CalendaringParameters:
    roll_gap: float
    roll_pressure: float
    temperature: float # (25)
    roll_speed: float
    dry_thickness: float
    initial_porosity: float

class CalendaringMachine(BaseMachine):
    def __init__(self, calendaring_model, calendaring_parameters):
        super().__init__("Calendaring", calendaring_model, calendaring_parameters)

    def run(self):
        self.turn_on()
        all_results = []

        for t in range(60):
            self.total_time = t
            proc = self.battery_model.update_properties(self.machine_parameters)
            result = self.get_current_properties(process_specifics=proc)
            all_results.append(result)
            self.save_data_to_local_folder()

        self.save_all_results(all_results)
        self.turn_off()

    def get_output(self):
        return self.battery_model.get_properties()
