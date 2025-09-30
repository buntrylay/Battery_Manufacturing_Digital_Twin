import time
import numpy as np
from simulation.process_parameters.Parameters import MixingParameters
from simulation.battery_model.MixingModel import MixingModel
from simulation.machine.BaseMachine import BaseMachine
from dataclasses import asdict
import sys
import os

# Add the server path to import notification functions
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'server'))
from notification_queue import notify_machine_status


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

    def receive_model_from_previous_process(self, initial_mixing_model: MixingModel):
        self.battery_model = initial_mixing_model

    def __mix_component(
        self,
        material_type,
        step_percent=0.02,
        pause_sec=0.1,
        duration_sec=10,
        results_list=None,
    ):
        total_volume_of_material_to_add = self.mixing_tank_volume * getattr(
            self.machine_parameters, f"{material_type}_ratio"
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
            # Notify that mixing process is starting
            notify_machine_status(
                machine_id="mixing",
                line_type=self.process_name.split('_')[1],  # Extract anode/cathode from process_name
                process_name=self.process_name,
                status="running",
                data={"stage": "starting", "message": "Mixing process started"}
            )
            
            self.turn_on()
            self.battery_model.add(
                "solvent",
                self.mixing_tank_volume * self.machine_parameters.solvent_ratio,
            )
            
            # Notify that solvent has been added
            notify_machine_status(
                machine_id="mixing",
                line_type=self.process_name.split('_')[1],
                process_name=self.process_name,
                status="running",
                data={"stage": "solvent_added", "message": "Solvent added to mixing tank"}
            )
            
            all_results = []
            
            # Mix PVDF with notifications
            notify_machine_status(
                machine_id="mixing",
                line_type=self.process_name.split('_')[1],
                process_name=self.process_name,
                status="running",
                data={"stage": "mixing_pvdf", "message": "Mixing PVDF binder"}
            )
            self.__mix_component("PVDF", duration_sec=8, results_list=all_results)
            
            # Mix CA with notifications
            notify_machine_status(
                machine_id="mixing",
                line_type=self.process_name.split('_')[1],
                process_name=self.process_name,
                status="running",
                data={"stage": "mixing_ca", "message": "Mixing conductive additive (CA)"}
            )
            self.__mix_component("CA", duration_sec=8, results_list=all_results)
            
            # Mix AM with notifications
            notify_machine_status(
                machine_id="mixing",
                line_type=self.process_name.split('_')[1],
                process_name=self.process_name,
                status="running",
                data={"stage": "mixing_am", "message": "Mixing active material (AM)"}
            )
            self.__mix_component("AM", duration_sec=10, results_list=all_results)
            
            self.save_all_results(all_results)
            
            # Notify that mixing process is completed
            notify_machine_status(
                machine_id="mixing",
                line_type=self.process_name.split('_')[1],
                process_name=self.process_name,
                status="completed",
                data={"stage": "completed", "message": "Mixing process completed successfully"}
            )
            
            self.turn_off()

    def turn_on(self):
        """Turn on the machine with notification."""
        super().turn_on()
        # Notify machine is turned on
        notify_machine_status(
            machine_id="mixing",
            line_type=self.process_name.split('_')[1],
            process_name=self.process_name,
            status="idle",
            data={"stage": "turned_on", "message": "Mixing machine turned on"}
        )

    def turn_off(self):
        """Turn off the machine with notification."""
        super().turn_off()
        # Notify machine is turned off
        notify_machine_status(
            machine_id="mixing",
            line_type=self.process_name.split('_')[1],
            process_name=self.process_name,
            status="idle",
            data={"stage": "turned_off", "message": "Mixing machine turned off"}
        )

    def validate_parameters(self, parameters: dict):
        return MixingParameters(**parameters).validate_parameters()
