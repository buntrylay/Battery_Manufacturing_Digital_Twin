from simulation.machine.BaseMachine import BaseMachine
from dataclasses import dataclass

@dataclass
# initialize parameters
class ElectrolyteFillingParameters:
    Vacuum_level: float
    Vacuum_filling : float
    Soaking_time: float

class ElectrolyteFillingMachine(BaseMachine):
    def __init__(self, 
        electrolyte_filling_model, 
        machine_parameters,
        connection_string=None
    ):
        super().__init__("ElectrolyteFilling",
            electrolyte_filling_model,
            machine_parameters,
            connection_string
        )

    def run(self):
        self.turn_on()
        all_results = []

        # the range can be adjusted based on real process time
        for t in range(self.machine_parameters.Soaking_time):
            self.total_time = t
            self.battery_model.update_properties(self.machine_parameters, t)
            proc = self.battery_model.get_properties()                     
            result = self.get_current_properties(process_specifics=proc)   
            all_results.append(result)
            self.save_data_to_local_folder()
        self.save_all_results(all_results)
        self.turn_off()

    def get_output(self):
        return self.battery_model.get_properties()