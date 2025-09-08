from simulation.machine.BaseMachine import BaseMachine
from dataclasses import dataclass
from simulation.process_parameters.Parameters import FormationCyclingParameters

class FormationCyclingMachine(BaseMachine):
    def __init__(self,
        formation_model,
        machine_parameters: FormationCyclingParameters,
        connection_string=None
    ):
        super().__init__("FormationCycling",
            formation_model,
            machine_parameters,
            connection_string
        )

    def run(self):
        self.turn_on()
        all_results = []

        for t in range(self.machine_parameters.Formation_duration_s + 1):
            self.total_time = t
            self.battery_model.update_properties(self.machine_parameters, t)
            proc = self.battery_model.get_properties()
            result = self.get_current_properties(process_specifics=proc)
            all_results.append(result)
            self.save_data_to_local_folder()

            # stop early if reached voltage limit
            if proc["Voltage_V"] >= self.machine_parameters.Charge_voltage_limit_V:
                break

        self.save_all_results(all_results)
        self.turn_off()
