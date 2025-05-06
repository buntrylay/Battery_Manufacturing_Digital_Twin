from Factory import Factory
from Slurry import Slurry
from Machines import MixingMachine

user_input_anode = {"PVDF": 0.05, "CB": 0.045, "AM": 0.495, "NMP": 0.41}

slurry = Slurry(200)
factory = Factory()
anode_mixing_machine = MixingMachine("TK_Mix_Anode", "Anode", slurry, user_input_anode)

factory.add_machine(anode_mixing_machine)
factory.start_simulation()