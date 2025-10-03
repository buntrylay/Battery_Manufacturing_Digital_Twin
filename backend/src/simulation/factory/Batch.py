from simulation.battery_model import (
    BaseModel,
    MixingModel,
    ElectrodeInspectionModel,
    RewindingModel,
)
from simulation.process_parameters.MixingParameters import MixingParameters, MaterialRatios


class Batch:
    def __init__(self, batch_id: str, anode_mixing_params: dict = None, cathode_mixing_params: dict = None):
        self.batch_id = batch_id
        
        # Initialize models with mixing parameters if provided
        if anode_mixing_params:
            anode_ratios = MaterialRatios(
                AM=anode_mixing_params.get("AM", 0.25),
                CA=anode_mixing_params.get("CA", 0.25),
                PVDF=anode_mixing_params.get("PVDF", 0.25),
                solvent=anode_mixing_params.get("Solvent", 0.25)
            )
            self.anode_mixing_params = MixingParameters(material_ratios=anode_ratios)
        else:
            # Default parameters for anode (normalized to sum to 1.0)
            default_anode_ratios = MaterialRatios(AM=0.75, CA=0.075, PVDF=0.075, solvent=0.1)
            self.anode_mixing_params = MixingParameters(material_ratios=default_anode_ratios)
        
        if cathode_mixing_params:
            cathode_ratios = MaterialRatios(
                AM=cathode_mixing_params.get("AM", 0.25),
                CA=cathode_mixing_params.get("CA", 0.25),
                PVDF=cathode_mixing_params.get("PVDF", 0.25),
                solvent=cathode_mixing_params.get("Solvent", 0.25)
            )
            self.cathode_mixing_params = MixingParameters(material_ratios=cathode_ratios)
        else:
            # Default parameters for cathode (normalized to sum to 1.0)
            default_cathode_ratios = MaterialRatios(AM=0.6, CA=0.1, PVDF=0.2, solvent=0.1)
            self.cathode_mixing_params = MixingParameters(material_ratios=default_cathode_ratios)
        
        # Initialize the models
        self.anode_line_model: BaseModel = MixingModel("Anode")
        self.cathode_line_model: BaseModel = MixingModel("Cathode")
        self.cell_line_model = None

    def get_batch_state(self):
        return {
            "batch_id": self.batch_id,
            "anode_mixing_params": self.anode_mixing_params.get_parameters_dict(),
            "cathode_mixing_params": self.cathode_mixing_params.get_parameters_dict(),
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
