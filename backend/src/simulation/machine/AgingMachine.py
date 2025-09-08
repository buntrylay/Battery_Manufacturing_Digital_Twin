import simulation.machine.BaseMachine as BaseMachine
from dataclasses import dataclass

@dataclass
# initialize parameters
class AgingParameters:
    k_leak : float
    temperature: float
    aging_time_days: float

class AgingMachine(BaseMachine):

    def __init__(self, 
        aging_model, 
        machine_parameters,
        connection_string=None
    ):
        super().__init__("Aging",
            aging_model,
            machine_parameters,
            connection_string
        )

    def run(self):
        self.turn_on()
        all_results = []

        # the range can be adjusted based on real process time
        for t in range(0, int(self.machine_parameters.aging_time_days * 24 * 3600) + 1, 3600):
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