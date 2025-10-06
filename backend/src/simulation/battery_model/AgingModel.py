from simulation.process_parameters.Parameters import AgingParameters
from simulation.battery_model.BaseModel import BaseModel
from simulation.battery_model.FormationCyclingModel import FormationCyclingModel
import numpy as np


class AgingModel(BaseModel):
    def __init__(self, formation_model: FormationCyclingModel):
        self.SOC_0 = formation_model.sei_efficiency
        self.Q_cell = formation_model.capacity
        self.V_OCV = formation_model.voltage

        self.SOC = self.SOC_0
        self.I_leak = 0.0
        self.defect_risk = False

    def soc_decay(self, soc0, k_leak, t):
        return soc0 * np.exp(-k_leak * t)

    def ocv_drift(self, soc):
        return 3.0 + 1.2 * soc

    def leakage_current(self, k_leak):
        return k_leak * 1e-3

    def defect_check(self, soc, ocv, ileak, soc0):
        return {(self.V_OCV - ocv) > 0.1 or ileak > 0.0001 or soc < 0.95 * soc0}

    def update_properties(
        self, machine_parameters: AgingParameters, current_time_step: int
    ):
        self.SOC = self.soc_decay(
            self.SOC_0, machine_parameters.k_leak, current_time_step
        )
        self.V_OCV = self.ocv_drift(self.SOC)
        self.I_leak = self.leakage_current(machine_parameters.k_leak)
        self.defect_risk = self.defect_check(
            self.SOC, self.V_OCV, self.I_leak, self.SOC_0
        )

    def get_properties(self):
        return {
            "SOC": float(self.SOC),
            "Initial_SOC": float(self.SOC_0),
            "Final_OCV_V": float(self.V_OCV),
            "Leakage_Current_A": float(self.I_leak),
            "defect_risk": bool(self.defect_risk),
        }
