import queue
from threading import Thread
from typing import Union
from simulation.machine import MixingMachine, CoatingMachine
from simulation.machine.DryingMachine import DryingMachine
from simulation.machine.CalendaringMachine import CalendaringMachine
from simulation.machine.SlittingMachine import SlittingMachine
from simulation.machine.ElectrodeInspectionMachine import ElectrodeInspectionMachine
from simulation.battery_model import MixingModel, CoatingModel, DryingModel, CalendaringModel, SlittingModel, ElectrodeInspectionModel
from simulation.process_parameters import (
    CoatingParameters,
    MixingParameters,
    DryingParameters,
    CalendaringParameters,
    SlittingParameters,
    ElectrodeInspectionParameters,
)
from simulation.process_parameters.MixingParameters import MaterialRatios
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
           AM=1.495, CA=0.045, PVDF=0.05, solvent=0.41
        )
        default_mixing_parameters_cathode = MixingParameters(
            AM=0.013, CA=0.039, PVDF=0.598, solvent=0.35
        )
        default_coating_parameters = CoatingParameters(
            coating_speed=0.05, gap_height=200e-6, flow_rate=5e-6, coating_width=0.5
        )
        default_drying_parameters = DryingParameters(
            web_speed=0.05
        )
        default_calendaring_parameters = CalendaringParameters(
            roll_gap=100e-6,
            roll_pressure=5e6,
            temperature=80,
            roll_speed=0.1,
            dry_thickness=100e-6,
            initial_porosity=0.4,
        )
        default_slitting_parameters = SlittingParameters(
            blade_sharpness=1.0,
            slitting_speed=0.1,
            slitting_tension=50.0,
            target_width=0.5,
        )
        default_electrode_inspection_parameters = ElectrodeInspectionParameters(
            epsilon_width_max=0.1, 
            epsilon_thickness_max=10e-6, 
            B_max=2.0, 
            D_surface_max=3
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
            self.factory_structure[electrode_type]["drying"] = DryingMachine(
                process_name=f"drying_{electrode_type}",
                drying_parameters=default_drying_parameters,
            )
            self.factory_structure[electrode_type]["calendaring"] = CalendaringMachine(
                process_name=f"calendaring_{electrode_type}",
                calendaring_parameters=default_calendaring_parameters,
            )
            self.factory_structure[electrode_type]["slitting"] = SlittingMachine(
                process_name=f"slitting_{electrode_type}",
                slitting_parameters=default_slitting_parameters,
            )
            self.factory_structure[electrode_type]["inspection"] = ElectrodeInspectionMachine(
                process_name=f"inspection_{electrode_type}",
                electrode_inspection_parameters=default_electrode_inspection_parameters,
            )
            # drying, calendaring, slitting, inspection
        # TODO: create and append machines to merged line

    def run_electrode_line(
        self, electrode_type: Union["anode", "cathode"], battery_model: MixingModel  # type: ignore
    ):
        for stage in ["mixing", "coating", "drying", "calendaring", "slitting", "inspection"]:
            running_machine = self.factory_structure[electrode_type][stage]
            running_machine.input_model(battery_model)
            running_machine.run()
            battery_model = running_machine.battery_model
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
                target=self.run_electrode_line, 
                args=("anode", batch.anode_line_model)
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

    def add_batch(self, batch: Batch):
        self.batch_queue.put(batch)

    def get_machine_status(self, line_type: str, machine_id: str):
        return self.factory_structure[line_type][machine_id].get_current_state()

    def get_current_plant_state(self):
        pass
