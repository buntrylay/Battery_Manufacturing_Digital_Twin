from threading import Event, Thread
from typing import Callable, Union
from simulation.machine import (
    MixingMachine,
    CoatingMachine,
    DryingMachine,
    CalendaringMachine,
    SlittingMachine,
    ElectrodeInspectionMachine,
    RewindingMachine,
    ElectrolyteFillingMachine,
    FormationCyclingMachine,
    AgingMachine,
)

# All other process parameters come from Parameters.py (via __init__.py)
from simulation.process_parameters import (
    MixingParameters,
    CoatingParameters,
    DryingParameters,
    CalendaringParameters,
    SlittingParameters,
    ElectrodeInspectionParameters,
    RewindingParameters,
    ElectrolyteFillingParameters,
    FormationCyclingParameters,
    AgingParameters,
)
from simulation.factory.Batch import Batch
from simulation.event_bus.events import (
    EventBus,
    MachineEvent,
    PlantSimulationEventType,
)


class PlantSimulation:
    """
    This class is the main class for the plant simulation.
    It is responsible for the overall simulation of the plant.
    """

    def __init__(self, listeners: list[Callable[[MachineEvent], None]] = None):
        # array of batches requests (to be processed)
        self.batch_requests: list[any] = []
        # array of batches that are CURRENTLY BEING processed
        self.running_batches: list[any] = []
        # structure of the factory (to be used to create the machines) - hardcoded design.
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
        # the event bus for different components to interface with the other components.
        self.event_bus = EventBus()
        # initialise the factory structure with the default machines
        self.__initialise_default_factory_structure()

    def __initialise_default_factory_structure(self):
        default_mixing_parameters_anode = MixingParameters(
            AM_ratio=0.495, CA_ratio=0.045, PVDF_ratio=0.05, solvent_ratio=0.41
        )
        default_mixing_parameters_cathode = MixingParameters(
            AM_ratio=0.513, CA_ratio=0.039, PVDF_ratio=0.098, solvent_ratio=0.35
        )
        default_coating_parameters = CoatingParameters(
            coating_speed=0.05, gap_height=200e-6, flow_rate=5e-6, coating_width=0.5
        )
        default_drying_parameters = DryingParameters(web_speed=0.05)
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
            target_width=0.5,
            slitting_tension=50.0,
        )
        default_electrode_inspection_parameters = ElectrodeInspectionParameters(
            epsilon_width_max=0.1,
            epsilon_thickness_max=10e-6,
            B_max=2.0,
            D_surface_max=3,
        )
        default_rewinding_parameters = RewindingParameters(
            rewinding_speed=0.5,
            initial_tension=100.0,
            tapering_steps=0.3,
            environment_humidity=30.0,
        )
        default_electrolyte_filling_parameters = ElectrolyteFillingParameters(
            Vacuum_level=100,
            Vacuum_filling=60,
            Soaking_time=10,
        )
        default_formation_cycling_parameters = FormationCyclingParameters(
            Charge_current_A=0.05, Charge_voltage_limit_V=4.2, Initial_Voltage=1
        )
        default_aging_parameters = AgingParameters(
            k_leak=1e-8, temperature=25, aging_time_days=10
        )
        # Create and append machines to anode & cathode lines
        for electrode_type in ["anode", "cathode"]:
            self.factory_structure[electrode_type]["mixing"] = MixingMachine(
                process_name=f"mixing_{electrode_type}",
                mixing_parameters=(
                    default_mixing_parameters_anode
                    if electrode_type == "anode"
                    else default_mixing_parameters_cathode
                ),
                event_bus=self.event_bus,
            )
            self.factory_structure[electrode_type]["coating"] = CoatingMachine(
                process_name=f"coating_{electrode_type}",
                coating_parameters=default_coating_parameters,
                event_bus=self.event_bus,
            )
            self.factory_structure[electrode_type]["drying"] = DryingMachine(
                process_name=f"drying_{electrode_type}",
                drying_parameters=default_drying_parameters,
                event_bus=self.event_bus,
            )
            self.factory_structure[electrode_type]["calendaring"] = CalendaringMachine(
                process_name=f"calendaring_{electrode_type}",
                calendaring_parameters=default_calendaring_parameters,
                event_bus=self.event_bus,
            )
            self.factory_structure[electrode_type]["slitting"] = SlittingMachine(
                process_name=f"slitting_{electrode_type}",
                slitting_parameters=default_slitting_parameters,
                event_bus=self.event_bus,
            )
            self.factory_structure[electrode_type]["inspection"] = (
                ElectrodeInspectionMachine(
                    process_name=f"inspection_{electrode_type}",
                    electrode_inspection_parameters=default_electrode_inspection_parameters,
                    event_bus=self.event_bus,
                )
            )
        # Create and append cell line machines
        self.factory_structure["cell"]["rewinding"] = RewindingMachine(
            process_name="rewinding_cell",
            rewinding_parameters=default_rewinding_parameters,
            event_bus=self.event_bus,
        )
        self.factory_structure["cell"]["electrolyte_filling"] = (
            ElectrolyteFillingMachine(
                process_name="electrolyte_filling_cell",
                electrolyte_filling_parameters=default_electrolyte_filling_parameters,
                event_bus=self.event_bus,
            )
        )
        self.factory_structure["cell"]["formation_cycling"] = FormationCyclingMachine(
            process_name="formation_cycling_cell",
            formation_cycling_parameters=default_formation_cycling_parameters,
            event_bus=self.event_bus,
        )
        self.factory_structure["cell"]["aging"] = AgingMachine(
            process_name="aging_cell",
            aging_parameters=default_aging_parameters,
            event_bus=self.event_bus,
        )

    def __run_electrode_line(
        self, electrode_type: Union["anode", "cathode"], batch: Batch  # type: ignore
    ):
        """this function is to run the electrode line for a specific batch (part of __run_pipeline_on_batch)
        Needs further work to improve the efficiency of the simulation
        """
        model = getattr(batch, f"{electrode_type}_line_model")

        for stage in [
            "mixing",
            "coating",
            "drying",
            "calendaring",
            "slitting",
            "inspection",
        ]:
            # (1) get the machine in order in the electrode line
            running_machine = self.factory_structure[electrode_type][stage]
            # (2) For mixing stage, update machine parameters with batch-specific parameters
            if stage == "mixing":
                mixing_params = getattr(batch, f"{electrode_type}_mixing_params")
                running_machine.update_machine_parameters(mixing_params)
            # (3) input into the machine (could be from the previous stage or from the initial mixing machine)
            running_machine.receive_model_from_previous_process(model)
            running_machine.batch_id = batch.batch_id
            running_machine.calculate_total_steps()
            # (4) run the machine (start the simulation)
            running_machine.run_simulation(
                total_steps=running_machine.total_steps,
                pause_between_steps=0.1,
                verbose=True
            )
            # (5) update the batch model (local)
            model = running_machine.battery_model
            # (6) clean up the machine (turn off the machine and empty the battery model (possibly for the next batch))
            running_machine.clean_up()
            # (7) update the batch model (global)
            setattr(batch, f"{electrode_type}_line_model", model)

    def __run_assembled_cell_line(
        self,
        batch: Batch,
    ):
        """this function is to run the assembled cell line for a specific batch (part of __run_pipeline_on_batch)
        Needs further work to improve the efficiency of the simulation
        """
        model = batch.cell_line_model
        for stage in ["rewinding", "electrolyte_filling", "formation_cycling", "aging"]:
            # (1) get the machine in order in the cell line (which could be from the previous stage or from the initial rewinding machine)
            running_machine = self.factory_structure["cell"][stage]
            # (2) input into the machine (could be from the previous stage or from the initial rewinding machine)
            running_machine.receive_model_from_previous_process(model)
            running_machine.calculate_total_steps()
            # (3) run the machine (start the simulation)
            running_machine.run_simulation(
                total_steps=running_machine.total_steps,
                pause_between_steps=0.1,
                verbose=True
            )            
            # (4) update the batch model (local)
            model = running_machine.battery_model
            # (5) clean up the machine (turn off the machine and empty the battery model (possibly for the next batch))
            running_machine.clean_up()
            # (6) update the batch model (global)
            setattr(batch, f"cell_line_model", model)

    def __run_pipeline_on_batch(self, batch: Batch):
        # to simulate anode and cathode lines in parallel
        run_anode_thread = Thread(
            target=self.__run_electrode_line, args=("anode", batch)
        )
        run_cathode_thread = Thread(
            target=self.__run_electrode_line, args=("cathode", batch)
        )
        # start electrode lines' simulation in parallel
        run_anode_thread.start()
        # emit event for anode line processing start
        self.event_bus.emit_plant_simulation_event(
            PlantSimulationEventType.BATCH_STARTED_ANODE_LINE,
            {"batch_id": batch.batch_id},
        )
        run_cathode_thread.start()
        # emit event for cathode line processing start
        self.event_bus.emit_plant_simulation_event(
            PlantSimulationEventType.BATCH_STARTED_CATHODE_LINE,
            {"batch_id": batch.batch_id},
        )
        # wait for the electrode lines' simulation to finish in parallel
        run_anode_thread.join()
        # emit event for anode line processing completion
        self.event_bus.emit_plant_simulation_event(
            PlantSimulationEventType.BATCH_COMPLETED_ANODE_LINE,
            {"batch_id": batch.batch_id},
        )
        run_cathode_thread.join()
        # emit event for cathode line processing completion
        self.event_bus.emit_plant_simulation_event(
            PlantSimulationEventType.BATCH_COMPLETED_CATHODE_LINE,
            {"batch_id": batch.batch_id},
        )
        # assemble the cell line model
        batch.assemble_cell_line_model()
        # emit event for batch merged
        self.event_bus.emit_plant_simulation_event(
            PlantSimulationEventType.BATCH_MERGED, {"batch_id": batch.batch_id}
        )
        # assemble the cell line model
        batch.assemble_cell_line_model()
        # emit event for cell assembly start
        self.event_bus.emit_plant_simulation_event(
            PlantSimulationEventType.BATCH_STARTED_CELL_LINE,
            {"batch_id": batch.batch_id},
        )
        # run the assembled cell line
        self.__run_assembled_cell_line(batch)
        # emit event for complete batch completion
        self.event_bus.emit_plant_simulation_event(
            PlantSimulationEventType.BATCH_COMPLETED, {"batch_id": batch.batch_id}
        )
        return True

    def __get_machine(self, line_type: str, machine_id: str):
        if line_type not in self.factory_structure:
            raise ValueError(f"Line type '{line_type}' is not found")
        elif machine_id not in self.factory_structure[line_type]:
            raise ValueError(f"Machine '{machine_id}' is not found")
        else:
            return self.factory_structure[line_type][machine_id]

    def add_batch(self, batch: Batch):
        if len(self.batch_requests) >= 3:
            raise ValueError("Maximum number of batches reached")
        else:
            self.batch_requests.append(batch)

    def run(self, out_of_batch_event: Event = None):
        """this function is to run the pipeline for a specific batch (part of __run_pipeline_on_batch)"""
        while self.batch_requests:
            # check the mixing machines
            anode_mixing_machine = self.factory_structure["anode"]["mixing"].state
            cathode_mixing_machine = self.factory_structure["cathode"]["mixing"].state
            if not anode_mixing_machine and not cathode_mixing_machine:
                batch = self.batch_requests.pop(0)
                self.__run_pipeline_on_batch(batch)
                # add the batch to the running batches
                self.running_batches.append(batch)
                # remove the batch from the running batches
                self.running_batches.remove(batch)
        if out_of_batch_event:
            out_of_batch_event.set()

    def get_machine_status(self, line_type: str, machine_id: str):
        machine = self.__get_machine(line_type, machine_id)
        return machine.get_current_state()

    def get_current_plant_state(self):
        batch_requests = [batch.get_batch_state() for batch in self.batch_requests]
        running_batches = [batch.get_batch_state() for batch in self.running_batches]
        machine_statuses = [
            self.factory_structure[line_type][machine_id].get_current_state()
            for line_type in self.factory_structure
            for machine_id in self.factory_structure[line_type]
        ]
        return {
            "batch_requests": batch_requests,
            "running_batches": running_batches,
            "machine_statuses": machine_statuses,
        }

    def reset_plant(self):
        self.batch_requests = []
        self.running_batches = []
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
        self.__initialise_default_factory_structure()
        return True

    def update_machine_parameters(self, line_type: str, machine_id: str, parameters):
        """Update parameters for a specific machine."""
        machine = self.__get_machine(line_type, machine_id)
        if machine.state:
            raise ValueError("Machine is running, cannot update parameters")
        machine.validate_parameters(parameters)
        machine.update_machine_parameters(parameters)
        return True

    def get_event_bus(self):
        """Get the event bus instance."""
        return self.event_bus
