import queue
from threading import Thread
from typing import Union
from simulation.machine.DryingMachine import DryingParameters
from simulation.machine import MixingMachine, CoatingMachine
from simulation.battery_model import MixingModel, CoatingModel
from simulation.process_parameters import CoatingParameters, MixingParameters
from simulation.process_parameters.MixingParameters import MaterialRatios
from simulation.factory.Batch import Batch


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
        # initialise default mixing parameters
        default_mixing_parameters_anode = MixingParameters(
            MaterialRatios(AM=0.495, CA=0.045, PVDF=0.05, solvent=0.41)
        )
        default_mixing_parameters_cathode = MixingParameters(
            MaterialRatios(AM=0.013, CA=0.039, PVDF=0.598, solvent=0.35)
        )
        default_coating_parameters = CoatingParameters(
            coating_speed=0.05, gap_height=200e-6, flow_rate=5e-6, coating_width=0.5
        )
        default_drying_parameters = DryingParameters(
            V_air=1.0, H_air=80, drying_length=10, web_speed=0.05
        )
        # create and append machines to electrode lines
        for electrode_type in ["anode", "cathode"]:
            self.factory_structure[electrode_type]["mixing"] = MixingMachine(
                process_name=f"mixing_{electrode_type}",
                mixing_parameters=(
                    default_mixing_parameters_anode
                    if electrode_type == "anode"
                    else default_mixing_parameters_cathode
                ),
            )
            self.factory_structure[electrode_type]["coating"] = CoatingMachine(
                process_name=f"coating_{electrode_type}",
                coating_parameters=default_coating_parameters,
            )
            # drying, calendaring, slitting, inspection
        # TODO: create and append machines to merged line

    def run_electrode_line(
        self, electrode_type: Union["anode", "cathode"], battery_model: MixingModel  # type: ignore
    ):
        for stage in ["mixing", "coating"]:
            running_machine = self.factory_structure[electrode_type][stage]
            running_machine.input_model(battery_model)
            running_machine.run()
        # TODO: drying, calendaring, slitting, inspection

    def run_cell_line(
        self,
        electrode_inspection_model_anode: MixingModel,
        electrode_inspection_model_cathode: MixingModel,
    ):
        # TODO: rewinding, electrolyte_filling, formation_cycling, aging
        pass

    def run_pipeline(self):
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
