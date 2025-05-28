from ..state.electrode_type import ElectrodeType
from .base_process import Simulation
from ..state import Slurry
from ..calc import MixingPropertyCalculator
import time
import random


class MixingConfiguration:
    def __init__(
        self,
        electrode_type: ElectrodeType,
        binder_ratio: float,
        ca_ratio: float,
        am_ratio: float,
        h2o_ratio: float,
    ):
        # Slurry configuration
        self.electrode_type = electrode_type  # cathode or anode

        # Slurry component ratios. Can be set by the user.
        self.material_ratios = {
            "binder": binder_ratio,
            "ca": ca_ratio,
            "am": am_ratio,
            "solvent": h2o_ratio,
        }

        # if the user does not provide the ratios, use the default values
        if self.electrode_type == ElectrodeType.Cathode:
            self.binder_ratio = 0.013
            self.ca_ratio = 0.039
            self.am_ratio = 0.598
            self.solvent_ratio = 0.35
        elif self.electrode_type == ElectrodeType.Anode:
            self.binder_ratio = 0.013
            self.ca_ratio = 0.039
            self.am_ratio = 0.598
            self.solvent_ratio = 0.35

        # machine parameters
        self.mixing_tank_volume = 200  # in litres
        self.machine_rpm = 400
        self.machine_temperature = 20
        self.machine_pressure = 1

        # simulation parameters
        self.percentage_per_step_for_binder = 0.02  # 2% of the total binder volume
        self.percentage_per_step_for_ca = 0.02  # 2% of the total CA volume
        self.percentage_per_step_for_am = 0.02  # 2% of the total AM volume

        self.pause_per_step = 3 # in seconds. use by the Simulation base class to pause the simulation


class MixingProcess(Simulation):
    """
    A process class for simulating the mixing of battery slurry components.

    This class handles the stepwise addition of components to a slurry in a specific order:
    1. Solvent (H2O for anode, NMP for cathode)
    2. PVDF binder
    3. Conductive additive (CA)
    4. Active material (AM)
    """

    def __init__(
        self,
        id: str,
        mixing_configuration: MixingConfiguration,
        mixing_calculator: MixingPropertyCalculator,
    ):
        super().__init__(id, 130, 10)
        # 130 mins is the actual process duration, x10 is the speed factor
        self.slurry = Slurry()
        self.mixing_configuration = mixing_configuration
        self.mixing_calculator = mixing_calculator

        # initialise the slurry with solvent right away
        print(
            f"DEBUG: Current time: {self.current_time}: Initialsing slurry (machine) with solvent"
        )

        self.slurry.add(
            "solvent",
            self.mixing_configuration.mixing_tank_volume
            * self.mixing_configuration.solvent_ratio,
        )

    def calculate_total_steps(self) -> int:
        """Calculate the total number of steps for this mixing process."""
        # Calculate total steps needed to add each material in 2% increments
        # So usually, adding binder will take 40 mins, CA will take 30 mins, and AM will take 60 mins

        # calculate the total steps to add binder: 2% of the total binder volume each step
        total_steps_to_add_binder = int(
            (
                self.mixing_configuration.mixing_tank_volume
                * self.mixing_configuration.binder_ratio
            )
            / (
                self.mixing_configuration.mixing_tank_volume
                * self.mixing_configuration.binder_ratio
                * self.mixing_configuration.percentage_per_step_for_binder
            )
        )
        # calculate the total steps to add CA: 2% of the total CA volume each step
        total_steps_to_add_ca = int(
            (
                self.mixing_configuration.mixing_tank_volume
                * self.mixing_configuration.ca_ratio
            )
            / (
                self.mixing_configuration.mixing_tank_volume
                * self.mixing_configuration.ca_ratio
                * self.mixing_configuration.percentage_per_step_for_ca
            )
        )
        # calculate the total steps to add AM: 2% of the total AM volume each step
        total_steps_to_add_am = int(
            (
                self.mixing_configuration.mixing_tank_volume
                * self.mixing_configuration.am_ratio
            )
            / (
                self.mixing_configuration.mixing_tank_volume
                * self.mixing_configuration.am_ratio
                * self.mixing_configuration.percentage_per_step_for_am
            )
        )

        # total steps is the sum of all the steps
        total_steps = (
            total_steps_to_add_binder + total_steps_to_add_ca + total_steps_to_add_am
        )

        # return the total steps
        return total_steps

    def step_logic(self, t: int) -> None:
        """
        Execute one step of the mixing process.

        Args:
            t (int): Current simulation time step
        """

        # add Binder for 40 mins (30.72% of the total simulation time)
        if (
            self.slurry.binder
            < self.mixing_configuration.binder_ratio
            * self.mixing_configuration.mixing_tank_volume
        ):
            self.slurry.add(
                "PVDF",
                self.mixing_configuration.mixing_tank_volume
                * self.mixing_configuration.binder_ratio
                * 0.5,
            )
        # add CA for 30 mins (29.85% of the total simulation time)
        elif t < self.simulation_time * (30 / 130):
            self.slurry.add(
                "CA",
                self.mixing_configuration.mixing_tank_volume
                * self.mixing_configuration.ca_ratio,
            )
        # add AM for 60 mins (49.43% of the total simulation time)
        elif t < self.simulation_time * (60 / 130):
            self.slurry.add(
                "AM",
                self.mixing_configuration.mixing_tank_volume
                * self.mixing_configuration.am_ratio,
            )

        # Get current state as dictionary
        state_data = self.slurry.as_dict()

        # Calculate new properties
        updated_properties = self.calculator.calculate_properties(state_data)

        # Update state with new properties
        self.slurry.update_properties(
            updated_properties["viscosity"],
            updated_properties["density"],
            updated_properties["yield_stress"],
        )

    def add_material(self, material_type: str, volume: float) -> None:
        """Add a material to the slurry."""
        self.slurry.add(material_type, volume)


simu = MixingProcess("test", 
        MixingConfiguration(
            electrode_type=ElectrodeType.Anode, 
            binder_ratio=0.013, 
            ca_ratio=0.039, 
            am_ratio=0.598, 
            h2o_ratio=0.35), 
        MixingPropertyCalculator())


simu.run()