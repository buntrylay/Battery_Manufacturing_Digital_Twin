from simulation.machine.BaseMachine import BaseMachine
from dataclasses import dataclass
from simulation.process_parameters.Parameters import SlittingParameters
from simulation.battery_model import CalendaringModel  
from simulation.battery_model.SlittingModel import SlittingModel

class SlittingMachine(BaseMachine):
    def __init__(
        self, 
        process_name: str,
        slitting_parameters: SlittingParameters,
        slitting_model: SlittingModel = None, 
        connection_string=None
    ):
        super().__init__(
            process_name,
            slitting_model, 
            slitting_parameters, 
            connection_string
        )
    def input_model(self, previous_model: CalendaringModel):
        self.battery_model = SlittingModel(previous_model)
    def run(self):
        self.turn_on()
        all_results = []

        for t in range(30):
            self.total_time = t
            self.battery_model.update_properties(self.machine_parameters)
            result = self.get_current_state()   
            all_results.append(result)
            self.save_data_to_local_folder()
        self.save_all_results(all_results)
        self.turn_off()