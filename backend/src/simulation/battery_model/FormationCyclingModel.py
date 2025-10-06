from simulation.process_parameters.Parameters import FormationCyclingParameters
from simulation.battery_model.BaseModel import BaseModel
from simulation.battery_model.ElectrolyteFillingModel import ElectrolyteFillingModel
import numpy as np


class FormationCyclingModel(BaseModel):
    def __init__(self, filling_model: ElectrolyteFillingModel):
        self.eta_wetting = filling_model.eta_wetting
        self.volume_elec = filling_model.V_elec_filling
        # state
        self.voltage = 0.0
        self.capacity = 0.0
        self.sei_efficiency = 0.0
        # constants
        self.Q_theoretical_Ah = 2.0
        self.k_sei = 0.05
        self.t50 = 300

    def update_properties(
        self, machine_parameters: FormationCyclingParameters, current_time_step: int
    ):
        self.sei_efficiency = float(
            1 / (1 + np.exp(-self.k_sei * (current_time_step - self.t50)))
        )
        self.capacity = self.sei_efficiency * self.Q_theoretical_Ah * self.eta_wetting
        self.voltage = min(
            machine_parameters.initial_voltage
            + (machine_parameters.charge_current_A * current_time_step)
            / (self.capacity + 1e-6),
            machine_parameters.charge_voltage_limit_V,
        )

    def get_properties(self):
        return {
            "Voltage_V": self.voltage,
            "Capacity_Ah": self.capacity,
            "sei_efficiency": self.sei_efficiency,
            "Eta wetting": self.eta_wetting,
            "Volume_electrolyte": self.volume_elec,
        }
