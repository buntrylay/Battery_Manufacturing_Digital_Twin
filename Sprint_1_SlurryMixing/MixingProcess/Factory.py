from Slurry import Slurry
from Machines import MixingMachine

class Factory:
    def __init__(self, slurry):
        self.machines = []

    def add_machine(self, machine):
        self.machines.append(machine)

    def start_simulation(self):
        for machine in self.machines:
            machine.turn_on()
            machine.run()
            machine.turn_off()