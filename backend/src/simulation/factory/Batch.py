from simulation.battery_model import (
    BaseModel,
    MixingModel,
    ElectrodeInspectionModel,
    RewindingModel,
)


class Batch:
    def __init__(self, batch_id: str):
        self.batch_id = batch_id
        # Initialise the models
        self.__anode_line_model: BaseModel = MixingModel("Anode")  #
        self.__cathode_line_model: BaseModel = MixingModel("Cathode")  #
        self.__cell_line_model = None

    def get_batch_state(self):
        return {
            "batch_id": self.batch_id,
            "current_anode_line_model": self.__anode_line_model.get_properties(),
            "current_cathode_line_model": self.__cathode_line_model.get_properties(),
            "current_cell_line_model": (
                self.__cell_line_model.get_properties()
                if self.__cell_line_model
                else None
            ),
        }

    def assemble_cell_line_model(self):
        assert isinstance(
            self.__anode_line_model, ElectrodeInspectionModel
        ), f"Anode model must be ElectrodeInspectionModel, got {type(self.__anode_line_model)}"
        assert isinstance(
            self.__cathode_line_model, ElectrodeInspectionModel
        ), f"Cathode model must be ElectrodeInspectionModel, got {type(self.__cathode_line_model)}"
        self.__cell_line_model = RewindingModel(
            self.__anode_line_model, self.__cathode_line_model
        )

    def get_batch_model(self, line_type):
        if line_type == "anode":
            return self.__anode_line_model
        elif line_type == "cathode":
            return self.__cathode_line_model
        elif line_type == "cell":
            return self.__cell_line_model
        else:
            raise ValueError("line_type not found")

    def update_batch_model(self, line_type, model):
        if line_type == "anode":
            self.__anode_line_model = model
        elif line_type == "cathode":
            self.__cathode_line_model = model
        elif line_type == "cell":
            self.__cell_line_model = model
        else:
            raise ValueError("line_type not found")
