from Slurry import Slurry
from Machines import MixingMachine

class Factory:
    def __init__(self):
        self.slurry = Slurry(volume=200)
        self.mixer = MixingMachine(self.slurry)

    def start_simulation(self):
        self.mixer.run()