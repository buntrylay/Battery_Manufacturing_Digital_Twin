from simulation.battery_model.CoatingModel import CoatingModel
from simulation.battery_model.BaseModel import BaseModel


class DryingModel(BaseModel):
    def __init__(self, coating_model: CoatingModel):
        self.wet_thickness = coating_model.wet_thickness # wet thickness, taken from coating model's wet thickness
        self.solid_content = coating_model.solid_content # solid content, taken from coating model's solid content


        # calculated properties
        self.dry_thickness = 0 # dry thickness (m) ??? is this from the CoatingModel?
        self.mass_solvent = 0
        self.evaporation_rate = 0
        self.coating_thickness = 0 # coating thickness (m)
        self.defect_risk = False # defect risk (bool)


    def update_properties(self):
        pass

    def get_properties(self):
        pass