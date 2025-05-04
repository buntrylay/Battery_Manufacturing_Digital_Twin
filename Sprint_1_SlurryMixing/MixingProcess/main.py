from Factory import Factory
from Slurry import Slurry
from Machines import MixingMachine

slurry = Slurry(200)
factory = Factory(slurry)
factory.add_machine(MixingMachine(slurry))
factory.start_simulation()