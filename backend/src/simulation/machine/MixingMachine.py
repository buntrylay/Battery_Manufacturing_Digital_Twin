import time
import numpy as np
from simulation.process_parameters.Parameters import MixingParameters
from simulation.battery_model.MixingModel import MixingModel
from simulation.machine.BaseMachine import BaseMachine

# Import notification functions
try:
    # Try multiple import paths to handle different environments
    try:
        from server.notification_queue import notify_machine_status
    except ImportError:
        from backend.src.server.notification_queue import notify_machine_status
except ImportError:
    # Fallback if import fails
    def notify_machine_status(*args, **kwargs):
        print("No server is running")
        pass


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
    ):
        total_volume_of_material_to_add = self.mixing_tank_volume * getattr(
            self.machine_parameters, f"{material_type}_ratio"
        )
        volume_added_in_each_step = step_percent * total_volume_of_material_to_add
        added_volume = 0.0
        comp_start_time = self.total_time
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
            # broadcast data
            # websocket_manager.broadcast_data(self.get_current_state())
            # save data to database
            # postgres_helper.save_data_to_database(self.get_current_state())
            # notify_machine_status()
            time.sleep(pause_sec)

    def run(self):
        if self.pre_run_check():
            self.turn_on()
            # Notify start of mixing process
            notify_machine_status(
                machine_id=self.process_name,
                line_type=self.process_name.split("_")[-1],
                process_name=self.process_name,
                status="mixing_started",
                data={
                    "message": f"Starting {self.process_name} mixing process",
                    "tank_volume": self.mixing_tank_volume,
                },
            )

            # Add initial solvent
            solvent_volume = (
                self.mixing_tank_volume * self.machine_parameters.solvent_ratio
            )
            self.battery_model.add("solvent", solvent_volume)
            notify_machine_status(
                machine_id=self.process_name,
                line_type=self.process_name.split("_")[-1],
                process_name=self.process_name,
                status="solvent_added",
                data={
                    "message": f"Added {solvent_volume:.2f}L solvent",
                    "volume": solvent_volume,
                },
            )
            # Mix PVDF
            notify_machine_status(
                machine_id=self.process_name,
                line_type=self.process_name.split("_")[-1],
                process_name=self.process_name,
                status="component_mixing",
                data={
                    "message": "Starting PVDF mixing",
                    "component": "PVDF",
                    "duration": 8,
                },
            )
            self.__mix_component("PVDF", duration_sec=8)
            # Mix CA
            notify_machine_status(
                machine_id=self.process_name,
                line_type=self.process_name.split("_")[-1],
                process_name=self.process_name,
                status="component_mixing",
                data={
                    "message": "Starting CA mixing",
                    "component": "CA",
                    "duration": 8,
                },
            )
            self.__mix_component("CA", duration_sec=8)
            # Mix AM
            notify_machine_status(
                machine_id=self.process_name,
                line_type=self.process_name.split("_")[-1],
                process_name=self.process_name,
                status="component_mixing",
                data={
                    "message": "Starting AM mixing",
                    "component": "AM",
                    "duration": 10,
                },
            )
            self.__mix_component("AM", duration_sec=10)
            self.turn_off()

    def step_logic(self, t: int):
        if t == 0:
            self.battery_model.add("solvent", solvent_volume)
            notify_machine_status(
                machine_id=self.process_name,
                line_type=self.process_name.split("_")[-1],
                process_name=self.process_name,
                status="solvent_added",
                data={
                    "message": f"Added {solvent_volume:.2f}L solvent",
                    "volume": solvent_volume,
                },
            )
        elif t <= 100:
            self.__mix_component("PVDF", duration_sec=8)
        elif t <= 200:
            self.__mix_component("CA", duration_sec=8)
        elif t <= 300:
            self.__mix_component("AM", duration_sec=10)

    def validate_parameters(self, parameters: dict):
        return MixingParameters(**parameters).validate_parameters()
