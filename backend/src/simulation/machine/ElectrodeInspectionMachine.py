from simulation.machine.BaseMachine import BaseMachine
from dataclasses import dataclass

@dataclass
# initialize parameters
class ElectrodeInspectionParameters:
    epsilon_width_max: float
    epsilon_thickness_max: float
    B_max: float
    D_surface_max: float


class ElectrodeInspectionMachine(BaseMachine):

    def __init__(self, 
        electrode_inspection_model, 
        machine_parameters,
        connection_string=None
    ):
        super().__init__("ElectrodeInspection",
            electrode_inspection_model,
            machine_parameters,
            connection_string
        )

    def run(self):
        self.turn_on()
        all_results = []

        # the range can be adjusted based on real process time
        for t in range(10):
            self.total_time = t
            self.battery_model.update_properties(self.machine_parameters)
            proc = self.battery_model.get_properties()                     
            result = self.get_current_properties(process_specifics=proc)   
            all_results.append(result)
            self.save_data_to_local_folder()
        self.save_all_results(all_results)
        self.turn_off()
