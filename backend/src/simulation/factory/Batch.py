from simulation.battery_model import MixingModel


class Batch:
    def __init__(self, id: str):
        self.mixing_model_anode = MixingModel("Anode")
        self.mixing_model_cathode = MixingModel("Cathode")