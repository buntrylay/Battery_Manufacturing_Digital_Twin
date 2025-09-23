import queue
from threading import Thread
from typing import Union
from simulation.machine import MixingMachine, CoatingMachine
from simulation.battery_model import MixingModel, CoatingModel
from simulation.process_parameters import MixingParameters, CoatingParameters
from simulation.factory.Batch import Batch


class PlantSimulation:
    def __init__(self):
        self.batch_queue = queue.Queue()
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
            AM_ratio=1.495, CA_ratio=0.045, PVDF_ratio=0.05, solvent_ratio=0.41
        )
        default_mixing_parameters_cathode = MixingParameters(
            AM_ratio=0.598, CA_ratio=0.039, PVDF_ratio=0.013, solvent_ratio=0.35
        )
        default_coating_parameters = CoatingParameters(
            coating_speed=0.05, gap_height=200e-6, flow_rate=5e-6, coating_width=0.5
        )
        # TODO: Drying, Calendaring, Slitting, Inspection parameters
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
            # TODO: drying, calendaring, slitting, inspection
        # TODO: create and append machines to merged line

    def run_electrode_line(
        self, electrode_type: Union["anode", "cathode"], battery_model: MixingModel  # type: ignore
    ):
        for stage in ["mixing", "coating"]:
            running_machine = self.factory_structure[electrode_type][stage]
            running_machine.receive_model_from_previous_process(battery_model)
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
        """Run the pipeline. This is the main function that runs the pipeline."""
        batch = self.batch_queue.get()
        run_anode_thread = Thread(
            target=self.run_electrode_line, args=("anode", batch.anode_line_model)
        )
        run_cathode_thread = Thread(
            target=self.run_electrode_line,
            args=("cathode", batch.cathode_line_model),
        )
        run_anode_thread.start()
        run_cathode_thread.start()
        run_anode_thread.join()
        run_cathode_thread.join()
        self.run_cell_line(batch.anode_line_model, batch.cathode_line_model)
        return

    def add_batch(self, batch: Batch):
        self.batch_queue.put(batch)

    def get_machine_status(self, line_type: str, machine_id: str):
        return self.factory_structure[line_type][machine_id].get_current_state()

    def get_current_plant_state(self):
        pass
        # plant_state = {
        #     "batch_queue": self.batch_queue.qsize(),
        #     "factory_structure": self.factory_structure,
        # }
        # return plant_state

    def update_machine_parameters(self, line_type: str, machine_id: str, parameters):
        """Update parameters for a specific machine."""
        if line_type not in self.factory_structure:
            raise ValueError(f"Line type '{line_type}' not found")
        if machine_id not in self.factory_structure[line_type]:
            raise ValueError(f"Machine '{machine_id}' not found in line '{line_type}'")
        machine = self.factory_structure[line_type][machine_id]
        if machine is None:
            raise ValueError(f"Machine '{machine_id}' is not initialized")
        machine.validate_parameters(parameters)
        machine.update_machine_parameters(parameters)
        return True
