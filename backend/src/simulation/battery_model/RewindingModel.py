from simulation.process_parameters.Parameters import RewindingParameters
from simulation.battery_model.BaseModel import BaseModel
from simulation.battery_model.ElectrodeInspectionModel import ElectrodeInspectionModel
import numpy as np


class RewindingModel(BaseModel):
    def __init__(
        self,
        electrode_inspection_model_anode: ElectrodeInspectionModel,
        electrode_inspection_model_cathode: ElectrodeInspectionModel,
    ):
        # state
        self.L_wound = 0
        self.D_roll = 0
        self.H_roll = 0
        self.tau_rewind = 0
        self.D_core = 0.2
        # the thickness of the separator (m)
        self.separator_thickness = 20e-6

        # from inspection of the 2 electrodes and performing merging purpose
        self.delta_sl = (
            electrode_inspection_model_anode.final_thickness
            + electrode_inspection_model_cathode.final_thickness
            + self.separator_thickness
        )

        self.porosity = (
            electrode_inspection_model_anode.porosity
            + electrode_inspection_model_cathode.porosity
        ) / 2

        self.final_width = (
            electrode_inspection_model_anode.final_width
            + electrode_inspection_model_cathode.final_width
        ) / 2
        # alignment error between the two electrodes
        self.epsilon_width = abs(
            electrode_inspection_model_anode.final_width
            - electrode_inspection_model_cathode.final_width
        )

    def D_roll_calc(self, L_wound, delta_sl, D_core):
        return np.sqrt(D_core**2 + (4 * L_wound * delta_sl) / np.pi)

    def tau_rewind_calc(self, D_roll, tau_initial, n_taper, D_core):
        return tau_initial * (D_core / D_roll) ** n_taper

    def H_roll_calc(self, delta_sl, tau_rewind):
        return tau_rewind / delta_sl

    def update_properties(
        self, machine_parameters: RewindingParameters, current_time_step: int = None
    ):
        INTERVAL = 1
        self.L_wound += machine_parameters.rewinding_speed * INTERVAL
        self.D_roll = self.D_roll_calc(self.L_wound, self.delta_sl, self.D_core)
        self.tau_rewind = self.tau_rewind_calc(
            self.D_roll,
            machine_parameters.initial_tension,
            machine_parameters.tapering_steps,
            self.D_core,
        )
        self.H_roll = self.H_roll_calc(self.delta_sl, self.tau_rewind)

    def get_properties(self):
        return {
            "final_thickness": float(self.delta_sl),
            "porosity": float(self.porosity),
            "final_width": float(self.final_width),
            "epsilon_width": float(self.epsilon_width),
            "wound_length": float(self.L_wound),
            "roll_diameter": float(self.D_roll),
            "web_tension": float(self.tau_rewind),
            "roll_hardness": float(self.H_roll),
        }
