from simulation.event_bus.events import EventBus
from simulation.process_parameters.Parameters import MixingParameters
from simulation.battery_model.MixingModel import MixingModel
from simulation.machine.BaseMachine import BaseMachine
from dataclasses import asdict
import numpy as np


class MixingMachine(BaseMachine):

    def __init__(
        self,
        process_name: str,
        mixing_model: MixingModel = None,
        mixing_parameters: MixingParameters = None,
        event_bus: EventBus = None,
    ):
        super().__init__(process_name, mixing_model, mixing_parameters, event_bus)
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
        def calc_steps(sec): return int(sec / self.pause_secs)
        self.solvent_step = 1
        self.pvdf_step = calc_steps(self.duration_secs["PVDF"])
        self.ca_step = calc_steps(self.duration_secs["CA"])
        self.am_step = calc_steps(self.duration_secs["AM"])
        self.total_steps = (
            self.solvent_step + self.pvdf_step + self.ca_step + self.am_step
        )

    def step_logic(self, t: int, verbose: bool = False):
        solvent_ratio = self.machine_parameters.solvent_ratio
        pvdf_ratio = self.machine_parameters.PVDF_ratio
        ca_ratio = self.machine_parameters.CA_ratio
        am_ratio = self.machine_parameters.AM_ratio

        total_solvent = self.mixing_tank_volume * solvent_ratio
        total_pvdf = self.mixing_tank_volume * pvdf_ratio
        total_ca = self.mixing_tank_volume * ca_ratio
        total_am = self.mixing_tank_volume * am_ratio

        pvdf_per_step = total_pvdf / max(1, self.pvdf_step)
        ca_per_step = total_ca / max(1, self.ca_step)
        am_per_step = total_am / max(1, self.am_step)

        # Add solvent at the start
        if t == 0:
            self.battery_model.add("solvent", total_solvent)
            if verbose:
                print(f"[{self.process_name}] Added solvent {total_solvent:.2f}L")
        # Add pvdf
        elif 1 <= t <= self.pvdf_step:
            self.battery_model.add("PVDF", pvdf_per_step)
            self.battery_model.update_properties()
            if verbose and t % 10 == 0:
                print(f"[{self.process_name}] Mixing PVDF: step {t}/{self.pvdf_step}")
        # Add ca
        elif self.pvdf_step < t <= self.pvdf_step + self.ca_step:
            self.battery_model.add("CA", ca_per_step)
            self.battery_model.update_properties()
            if verbose and t % 10 == 0:
                print(f"[{self.process_name}] Mixing CA: step {t - self.pvdf_step}/{self.ca_step}")
        # Add am
        elif self.pvdf_step + self.ca_step < t <= self.total_steps:
            self.battery_model.add("AM", am_per_step)
            self.battery_model.update_properties()
            if verbose and t % 10 == 0:
                print(f"[{self.process_name}] Mixing AM: step {t - self.pvdf_step - self.ca_step}/{self.am_step}")

        if t == self.total_steps - 1:
            result = asdict(self.get_current_state())
            if self.event_bus:
                self.event_bus.publish("mixing_completed", result)
            if verbose:
                print(f"[{self.process_name}] Mixing completed")

    def validate_parameters(self, parameters: dict):
        return MixingParameters(**parameters).validate_parameters()
