from simulation.battery_model import BaseModel
from simulation.battery_model import ElectrodeInspectionModel


class RewindingModel(BaseModel):
    def __init__(self, inspection_model_anode: ElectrodeInspectionModel, inspection_model_cathode: ElectrodeInspectionModel):
        pass

    def update_properties(self):
        pass

    def get_properties(self):
        pass