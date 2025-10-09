from simulation.event_bus.events import EventBus, PlantSimulationEventType
from simulation.process_parameters.Parameters import MixingParameters
from simulation.battery_model.MixingModel import MixingModel
from simulation.machine.BaseMachine import BaseMachine
from dataclasses import asdict


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
        self.duration_secs = {"PVDF": 8, "CA": 8, "AM": 10}
        self.expected_total_amount_of_solvent = None
        self.expected_total_amount_of_PVDF = None
        self.expected_total_amount_of_CA = None
        self.expected_total_amount_of_AM = None
        self.pvdf_per_step = None
        self.ca_per_step = None
        self.am_per_step = None
        self.solvent_step = 1
        self.pvdf_step = None
        self.ca_step = None
        self.am_step = None

    def receive_model_from_previous_process(self, initial_mixing_model: MixingModel):
        self.battery_model = initial_mixing_model

    def calculate_total_steps(self):
        def calc_steps(sec):
            return int(sec / self.pause_between_steps)
        DURATION_SECS = {"PVDF": 8, "CA": 8, "AM": 10}
        self.solvent_step = 1
        self.pvdf_step = calc_steps(DURATION_SECS["PVDF"])
        self.ca_step = calc_steps(DURATION_SECS["CA"])
        self.am_step = calc_steps(DURATION_SECS["AM"])
        self.total_steps = (
            self.solvent_step + self.pvdf_step + self.ca_step + self.am_step
        )

    def reset_addition_configuration(self):
        self.expected_total_amount_of_solvent = None
        self.expected_total_amount_of_PVDF = None
        self.expected_total_amount_of_CA = None
        self.expected_total_amount_of_AM = None
        self.pvdf_per_step = None
        self.ca_per_step = None
        self.am_per_step = None

    def check_addition_configuration(self):
        return (
            self.expected_total_amount_of_solvent is not None
            or self.expected_total_amount_of_PVDF is not None
            or self.expected_total_amount_of_CA is not None
            or self.expected_total_amount_of_AM is not None
            or self.pvdf_per_step is not None
            or self.ca_per_step is not None
            or self.am_per_step is not None
        )

    def pre_run_check(self):
        super().pre_run_check()
        self.reset_addition_configuration()
        self.calculate_total_amount_to_add_for_each_material()
        self.calculate_per_step_additions()
        return self.check_addition_configuration()

    def calculate_total_amount_to_add_for_each_material(self):
        self.expected_total_amount_of_solvent = (
            self.mixing_tank_volume * self.machine_parameters.solvent_ratio
        )
        self.expected_total_amount_of_PVDF = (
            self.mixing_tank_volume * self.machine_parameters.PVDF_ratio
        )
        self.expected_total_amount_of_CA = (
            self.mixing_tank_volume * self.machine_parameters.CA_ratio
        )
        self.expected_total_amount_of_AM = (
            self.mixing_tank_volume * self.machine_parameters.AM_ratio
        )

    def calculate_per_step_additions(self):
        self.pvdf_per_step = self.expected_total_amount_of_PVDF / max(1, self.pvdf_step)
        self.ca_per_step = self.expected_total_amount_of_CA / max(1, self.ca_step)
        self.am_per_step = self.expected_total_amount_of_AM / max(1, self.am_step)

    def step_logic(self, t: int, verbose=False):
        if t == 0:
            self.battery_model.add("solvent", self.expected_total_amount_of_solvent)
        elif 1 <= t <= self.pvdf_step:
            if self.battery_model.PVDF < self.expected_total_amount_of_PVDF:
                self.battery_model.add("PVDF", self.pvdf_per_step)
        elif self.pvdf_step < t <= self.pvdf_step + self.ca_step:
            if self.battery_model.CA < self.expected_total_amount_of_CA:
                self.battery_model.add("CA", self.ca_per_step)
        elif self.pvdf_step + self.ca_step < t <= self.total_steps:
            if self.battery_model.AM < self.expected_total_amount_of_AM:
                self.battery_model.add("AM", self.am_per_step)

    def validate_parameters(self, parameters):
        if isinstance(parameters, MixingParameters):
            return parameters.validate_parameters()
        elif isinstance(parameters, dict):
            return MixingParameters(**parameters).validate_parameters()
        else:
            raise TypeError(f"Expected MixingParameters or dict, got {type(parameters)}")
