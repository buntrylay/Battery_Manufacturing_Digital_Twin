from simulation.event_bus.events import EventBus
from simulation.process_parameters.Parameters import MixingParameters
from simulation.battery_model.MixingModel import MixingModel
from simulation.machine.BaseMachine import BaseMachine


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
        event_bus: EventBus = None,
    ):
        """
        Initialise a new MixingMachine instance.

        Args:
            mixing_model (MixingModel): The mixing model to be used.
            mixing_parameters (MixingParameters): The mixing parameters to be used.
        """
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
        self.solvent_step = 0
        self.pvdf_step = 100
        self.ca_step = 100
        self.am_step = 100
        self.total_steps = (
            self.solvent_step + self.pvdf_step + self.ca_step + self.am_step
        )

    def step_logic(self, t: int, verbose: bool):
        solvent_volume = self.mixing_tank_volume * self.machine_parameters.solvent_ratio
        pvdf_volume = self.mixing_tank_volume * self.machine_parameters.PVDF_ratio
        ca_volume = self.mixing_tank_volume * self.machine_parameters.CA_ratio
        am_volume = self.mixing_tank_volume * self.machine_parameters.AM_ratio

        pvdf_per_step = pvdf_volume / max(1, self.pvdf_step)
        ca_per_step = ca_volume / max(1, self.ca_step)
        am_per_step = am_volume / max(1, self.am_step)

        # first add solvent
        if t == 0:
            self.battery_model.add("solvent", solvent_volume)
            pass
        # then add pvdf
        elif self.solvent_step <= t < self.solvent_step + self.pvdf_step:
            if t == self.solvent_step:
                pass
            self.battery_model.add("PVDF", pvdf_per_step)
        # then ca
        elif (
            self.solvent_step + self.pvdf_step
            <= t
            < self.solvent_step + self.pvdf_step + self.ca_step
        ):
            if t == self.solvent_step + self.pvdf_step:
                pass
            self.battery_model.add("CA", ca_per_step)
        # then am
        elif (
            self.solvent_step + self.pvdf_step + self.ca_step
            <= t
            < self.solvent_step + self.pvdf_step + self.ca_step + self.am_step
        ):
            if t == self.solvent_step + self.pvdf_step + self.ca_step:
                pass
            self.battery_model.add("AM", am_per_step)

    def validate_parameters(self, parameters: dict):
        return MixingParameters(**parameters).validate_parameters()
