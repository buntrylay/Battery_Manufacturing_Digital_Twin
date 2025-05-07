from Factory import Factory
from Slurry import Slurry
from Sprint_1_SlurryMixing.MixingProcess.Machine import MixingMachine

slurry = Slurry(200)
factory = Factory(slurry)
anode_mixing_machine = MixingMachine(slurry)
factory.add_machine(anode_mixing_machine)
factory.start_simulation()