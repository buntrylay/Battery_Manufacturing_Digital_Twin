from simulation.machine.BaseMachine import BaseMachine
from dataclasses import dataclass
from simulation.process_parameters.Parameters import RewindingParameters


class RewindingMachine(BaseMachine):
    def __init__(self,
        rewinding_model, 
        machine_parameters: RewindingParameters,
        connection_string=None
    ):
        super().__init__("Rewinding", 
            rewinding_model, 
            machine_parameters, 
            connection_string
        )
    def run(self, end_time=120, step=5):
        self.turn_on()
        all_results = []

        for t in range(0, end_time + 1, step):
            self.total_time = t
            self.battery_model.update_properties(self.machine_parameters)
            proc = self.battery_model.get_properties()                     
            result = self.get_current_properties(process_specifics=proc)   
            all_results.append(result)
            self.save_data_to_local_folder()
        self.save_all_results(all_results)
        self.turn_off()