from Slurry import Slurry
from Machines import MixingMachine
from ResultLogger import ResultLogger

class Factory:
    def __init__(self):
        self.slurry = Slurry(volume=200)
        self.mixer = MixingMachine(self.slurry)

    def start_simulation(self):
        self.mixer.run()
        logger = ResultLogger(self.mixer.results)
        logger.save_to_json("simulation_output/final_results.json")