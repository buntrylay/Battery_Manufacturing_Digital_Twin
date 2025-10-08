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
        self.pause_secs = 0.1  
        self.duration_secs = {
            "PVDF": 8,
            "CA": 8,
            "AM": 10
        }

    def receive_model_from_previous_process(self, initial_mixing_model: MixingModel):
        self.battery_model = initial_mixing_model

    def calculate_total_steps(self):
        self.total_steps = len(self.duration_secs.values())

    def step_logic(self, t: int):
        solvent_volume = self.mixing_tank_volume * self.machine_parameters.solvent_ratio
        pvdf_volume = self.mixing_tank_volume * self.machine_parameters.PVDF_ratio  
        ca_volume = self.mixing_tank_volume * self.machine_parameters.CA_ratio
        am_volume = self.mixing_tank_volume * self.machine_parameters.AM_ratio

        pvdf_per_step = pvdf_volume / max(1, self.pvdf_step)
        ca_per_step = ca_volume / max(1, self.ca_step)
        am_per_step = am_volume / max(1, self.am_step)

        # solvent
        if t == 0:
            self.battery_model.add("solvent", solvent_volume)
            # notify_machine_status(
            #     machine_id=self.process_name,
            #     line_type=self.process_name.split("_")[-1],
            #     process_name=self.process_name,
            #     status="solvent_added",
            #     data={"message": f"Added {solvent_volume:.2f}L solvent"}
            # )
            pass

        # pvdf
        elif self.solvent_step <= t < self.solvent_step + self.pvdf_step:
            if t == self.solvent_step:
                # notify_machine_status(
                #     machine_id=self.process_name,
                #     line_type=self.process_name.split("_")[-1],
                #     process_name=self.process_name,
                #     status="pvdf_started",
                #     data={"message": "Starting PVDF mixing"}
                # )
                pass
            self.battery_model.add("PVDF", pvdf_per_step)

        # ca
        elif self.solvent_step + self.pvdf_step <= t < self.solvent_step + self.pvdf_step + self.ca_step:
            if t == self.solvent_step + self.pvdf_step:
                # notify_machine_status(
                #     machine_id=self.process_name,
                #     line_type=self.process_name.split("_")[-1],
                #     process_name=self.process_name,
                #     status="ca_started",
                #     data={"message": "Starting CA mixing"}
                # )
                pass
            self.battery_model.add("CA", ca_per_step)
        # am
        elif self.solvent_step + self.pvdf_step + self.ca_step <= t < self.solvent_step + self.pvdf_step + self.ca_step + self.am_step: 
            if t == self.solvent_step + self.pvdf_step + self.ca_step:
                # notify_machine_status(
                #     machine_id=self.process_name,
                #     line_type=self.process_name.split("_")[-1],
                #     process_name=self.process_name,
                #     status="am_started",
                #     data={"message": "Starting AM mixing"}
                # )

                pass
            self.battery_model.add("AM", am_per_step)

    def validate_parameters(self, parameters: dict):
        return MixingParameters(**parameters).validate_parameters()


        
