from simulation.battery_model import (
    BaseModel,
    MixingModel,
    ElectrodeInspectionModel,
    RewindingModel,
)


class Batch:
    def __init__(self, batch_id: str):
        self.batch_id = batch_id
        self.anode_line_model: BaseModel = MixingModel("Anode")
        self.cathode_line_model: BaseModel = MixingModel("Cathode")
        self.cell_line_model = None

    def get_batch_state(self):
        return {
            "batch_id": self.batch_id,
            "current_anode_line_model": self.anode_line_model.get_properties(),
            "current_cathode_line_model": self.cathode_line_model.get_properties(),
            "current_cell_line_model": (
                self.cell_line_model.get_properties() if self.cell_line_model else None
            ),
        }

    def assemble_cell_line_model(self):
        assert isinstance(self.anode_line_model, ElectrodeInspectionModel)
        assert isinstance(self.cathode_line_model, ElectrodeInspectionModel)
        self.cell_line_model = RewindingModel(
            self.anode_line_model, self.cathode_line_model
        )
        # print(self.get_batch_state())