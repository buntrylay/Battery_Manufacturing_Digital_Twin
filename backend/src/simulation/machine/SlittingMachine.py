from simulation.machine.BaseMachine import BaseMachine
from dataclasses import dataclass
from simulation.process_parameters.Parameters import SlittingParameters


class SlittingMachine(BaseMachine):
    def __init__(self, 
        slitting_model, 
        machine_parameters: SlittingParameters,
        connection_string=None
    ):
        super().__init__("Slitting", 
            slitting_model, 
            machine_parameters, 
            connection_string
        )

    def run(self):
        self.turn_on()
        all_results = []

        for t in range(30):
            self.total_time = t
            self.battery_model.update_properties(self.machine_parameters)
            proc = self.battery_model.get_properties()                     
            result = self.get_current_properties(process_specifics=proc)   
            all_results.append(result)
            self.save_data_to_local_folder()
        self.save_all_results(all_results)
        self.turn_off()