from dataclasses import dataclass
from simulation.process_parameters import BaseMachineParameters


@dataclass
class MaterialRatios:
    AM: float
    CA: float
    PVDF: float
    solvent: float
    
    def get_dict(self):
        return {
            "AM": self.AM,
            "CA": self.CA,
            "PVDF": self.PVDF,
            "solvent": self.solvent
        }


@dataclass
class MixingParameters(BaseMachineParameters):
    material_ratios: MaterialRatios

    def validate_parameters(self):
        if (
            self.material_ratios.AM
            + self.material_ratios.CA
            + self.material_ratios.PVDF
            + self.material_ratios.solvent
            != 1
        ):
            raise ValueError("The sum of the material ratios must be 1")
        return True

    def get_parameters_dict(self):
        return self.material_ratios.get_dict()
    
    # Properties to match MixingMachine expectations
    @property
    def AM_ratio(self):
        return self.material_ratios.AM
    
    @property
    def CA_ratio(self):
        return self.material_ratios.CA
    
    @property
    def PVDF_ratio(self):
        return self.material_ratios.PVDF
    
    @property
    def solvent_ratio(self):
        return self.material_ratios.solvent
