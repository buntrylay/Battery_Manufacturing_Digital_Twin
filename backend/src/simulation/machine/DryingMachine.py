from dataclasses import dataclass
from simulation.machine.BaseMachine import BaseMachine


@dataclass
class DryingParameters:
    V_air: float
    T_dry: float
    H_air: float
    drying_length: float
    web_speed: float
    coating_width: float = 0.5
    h_air: float = 0.1
    density: float = 1500
    solvent_density: float = 800
    delta_t: float = 1
    max_safe_evap_rate: float = 0.004


class DryingMachine(BaseMachine):
    def __init__(self, drying_model, drying_parameters):
        super().__init__("Drying", drying_model, drying_parameters)

    def run(self):
        self.turn_on()
        all_results = []
        total_steps = self.battery_model.time_steps(self.machine_parameters)

        for t in range(total_steps):
            self.total_time = t
            proc = self.battery_model.update_properties(self.machine_parameters)
            result = self.get_current_properties(process_specifics=proc)
            all_results.append(result)
            self.save_data_to_local_folder()
        self.save_all_results(all_results)
        self.turn_off()
