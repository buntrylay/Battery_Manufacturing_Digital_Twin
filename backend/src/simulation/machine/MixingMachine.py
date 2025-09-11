import time
import numpy as np
from simulation.process_parameters.Parameters import MixingParameters
from simulation.battery_model.MixingModel import MixingModel
from simulation.machine.BaseMachine import BaseMachine
from dataclasses import asdict


class MixingMachine(BaseMachine):
    """
    A machine class for simulating the mixing of battery slurry components.

    This class handles the stepwise addition of components to a slurry, simulates
    process parameters (temperature, pressure, RPM), and generates real-time
    simulation data in JSON format. Utility methods are used for formatting results,
    writing output files, and printing process information.

    """

    def __init__(
        self,
        process_name: str,
        mixing_model: MixingModel = None,
        mixing_parameters: MixingParameters = None,
        connection_string=None,
    ):
        """
        Initialise a new MixingMachine instance.

        Args:
            mixing_model (MixingModel): The mixing model to be used.
            mixing_parameters (MixingParameters): The mixing parameters to be used.
        """
        super().__init__(
            process_name, mixing_model, mixing_parameters, connection_string
        )
        self.mixing_tank_volume = 200

    def input_model(self, previous_model: MixingModel):
        self.battery_model = previous_model

    def __mix_component(
        self,
        material_type,
        step_percent=0.02,
        pause_sec=0.1,
        duration_sec=10,
        results_list=None,
    ):
        total_volume_of_material_to_add = (
            self.mixing_tank_volume
            * getattr(self.machine_parameters, material_type)
        )
        volume_added_in_each_step = step_percent * total_volume_of_material_to_add
        added_volume = 0.0
        comp_start_time = self.total_time
        last_saved_time = time.time()
        last_saved_result = None
        while self.total_time - comp_start_time < duration_sec:
            self.total_time += pause_sec
            if added_volume < total_volume_of_material_to_add:
                add_amt = min(
                    volume_added_in_each_step,
                    total_volume_of_material_to_add - added_volume,
                )
                self.battery_model.add(material_type, add_amt)
                added_volume += add_amt
            self.battery_model.update_properties()
            result = self.get_current_state()
            results_list.append(result)
            now = time.time()
            if (
                now - last_saved_time >= 0.1 and result != last_saved_result
            ):  # Check if data has changed
                # self.send_json_to_iothub(result)  # Send to IoT Hub
                self.save_data_to_local_folder()  # Print to console
                last_saved_time = now
                last_saved_result = result
            time.sleep(pause_sec)

    def run(self):
        if self.pre_run_check():
            self.turn_on()
            self.battery_model.add(
                "solvent",
                self.mixing_tank_volume
                * self.machine_parameters.solvent
            )
            all_results = []
            self.__mix_component("PVDF", duration_sec=8, results_list=all_results)
            self.__mix_component("CA", duration_sec=8, results_list=all_results)
            self.__mix_component("AM", duration_sec=10, results_list=all_results)
            self.save_all_results(all_results)
            self.turn_off()
