from simulation.battery_model import MixingModel


class Batch:
    def __init__(self, batch_id: str):
        self.batch_id = batch_id
        self.anode_line_model = MixingModel("Anode")
        self.cathode_line_model = MixingModel("Cathode")
        self.cell_line_model = None