import queue
from threading import Thread
from typing import Union
from simulation.battery_model.MixingModel import MixingModel
from simulation.process_parameters.MixingParameters import (
    MaterialRatios,
    MixingParameters,
)
from simulation.factory.Batch import Batch
from simulation.machine.MixingMachine import MixingMachine

# from simulation.machine.CoatingMachine import CoatingMachine


class PlantSimulation:
    def __init__(self):
        self.batch_queue = queue.Queue()
        self.current_batch = None
        self.factory_structure = {
            "anode": {
                "mixing": None,
                "coating": None,
                "drying": None,
                "calendaring": None,
                "slitting": None,
                "inspection": None,
            },
            "cathode": {
                "mixing": None,
                "coating": None,
                "drying": None,
                "calendaring": None,
                "slitting": None,
                "inspection": None,
            },
            "cell": {
                "rewinding": None,
                "electrolyte_filling": None,
                "formation_cycling": None,
                "aging": None,
            },
        }
        self.initialise_default_factory_structure()

    def initialise_default_factory_structure(self):
        default_mixing_parameters_anode = MixingParameters(
            MaterialRatios(AM=0.495, CA=0.045, PVDF=0.05, solvent=0.41)
        )
        default_mixing_parameters_cathode = MixingParameters(
            MaterialRatios(AM=0.013, CA=0.039, PVDF=0.598, solvent=0.35)
        )
        for electrode_type in ["anode", "cathode"]:
            self.factory_structure[electrode_type]["mixing"] = MixingMachine(
                process_name=f"mixing_{electrode_type}",
                mixing_parameters=(
                    default_mixing_parameters_anode
                    if electrode_type == "anode"
                    else default_mixing_parameters_cathode
                )
            )

    def run_electrode_line(
        self, electrode_type: Union["anode", "cathode"], mixing_model: MixingModel # type: ignore
    ):
        self.factory_structure[electrode_type]["mixing"].add_model(mixing_model)
        self.factory_structure[electrode_type]["mixing"].run()
        # TODO: coating, drying, calendaring, slitting, inspection

    def run_cell_line(
        self,
        electrode_inspection_model_anode: MixingModel,
        electrode_inspection_model_cathode: MixingModel,
    ):
        # TODO: rewinding, electrolyte_filling, formation_cycling, aging
        pass

    def run(self):
        while self.batch_queue:
            batch = self.batch_queue.get()
            run_anode_thread = Thread(
                target=self.run_electrode_line, args=("anode", batch.mixing_model_anode)
            )
            run_cathode_thread = Thread(
                target=self.run_electrode_line,
                args=("cathode", batch.mixing_model_cathode),
            )
            run_anode_thread.start()
            run_cathode_thread.start()
            run_anode_thread.join()
            run_cathode_thread.join()

    def add_batch(self, batch: Batch):
        self.batch_queue.put(batch)

    def get_current_plant_state(self):
        pass
