from threading import Condition, Event, Thread, Lock
from typing import Callable, Optional
import uuid
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
    PlantSimulationEvent,
    PlantSimulationEventType,
)


class PlantSimulation:
    """
    This class is the main class for the plant simulation.
    It is responsible for the overall simulation of the plant.
    """

    def __init__(self, listeners: list[Callable[[PlantSimulationEvent], None]] = None):
        # Callables: regular function, method, lambda, functor object, taking an argument - PlantSimulation event
        # array of batches requests (to be processed). PROTECTED by pipeline_condition.
        self.__batch_request_list: list[Batch] = []
        # array of batches that are CURRENTLY BEING processed. PROTECTED by pipeline_condition.
        self.__running_batch_list: list[Batch] = []
        # track worker threads handling batch requests so we can await graceful shutdowns.
        # [str, Thread]: str refers to the batch id, Thread refers to the processing thread.
        # PROTECTED by pipeline_condition.
        self.__batch_worker_thread_list: dict[str, Thread] = {}
        # structure of the factory (to be used to create the machines) - hardcoded design.
        self.__factory_structure = {
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
        self.__event_bus = EventBus()
        # track the active batch associated with each machine
        self.__machine_batch_context: dict[str, str] = {}
        # runner thread management for background processing loop
        self.__runner_thread_lock = Lock()
        # this object can be None. This thread is a monitoring thread to keep track of all batch threads,
        # making sure the batch threads run with some sort of parent threads.
        self.__runner_thread: Optional[Thread] = None
        #
        self.__plant_is_idle_event = Event()
        # initially, no batch so that's why it is set
        self.__plant_is_idle_event.set()
        """ 
            Condition object: initialises a shared Condition used in __process_batch_request 
            to block batch-worker threads until they reach the queue front and both mixing machines are idle, 
            and to wake waiting workers when slots free up.
            This object also prevents concurrent accesses to the batch_requests, running_batches, and batch_worker_threads.
        """
        self.__access_pipeline_condition = Condition()
        # better than check the states of the mixing machines, which might entail some delays.
        self.__pipeline_is_ready = True
        # initialise the factory structure with the default machines
        self.__initialise_default_factory_structure()
        # machine-level locks to ensure only one batch uses a machine at a time
        self.__machine_lock_structure = {
            line_type: {stage: Lock() for stage in self.__factory_structure[line_type]}
            for line_type in self.__factory_structure
        }
        # FOR TESTING ONLY
        self.auto_generated_batch_id = 1

    def __initialise_default_factory_structure(self):
        # initialise the default parameters
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
            vacuum_level=100,
            vacuum_filling=60,
            soaking_time=10,
        )
        default_formation_cycling_parameters = FormationCyclingParameters(
            charge_current_A=0.05, charge_voltage_limit_V=4.2, initial_voltage=1
        )
        default_aging_parameters = AgingParameters(
            k_leak=1e-8, temperature=25, aging_time_days=10
        )
        # Create and append machines to anode & cathode lines
        for electrode_type in ["anode", "cathode"]:
            self.__factory_structure[electrode_type]["mixing"] = MixingMachine(
                process_name=f"mixing_{electrode_type}",
                mixing_parameters=(
                    default_mixing_parameters_anode
                    if electrode_type == "anode"
                    else default_mixing_parameters_cathode
                ),
                event_bus=self.__event_bus,
            )
            self.__factory_structure[electrode_type]["coating"] = CoatingMachine(
                process_name=f"coating_{electrode_type}",
                coating_parameters=default_coating_parameters,
                event_bus=self.__event_bus,
            )
            self.__factory_structure[electrode_type]["drying"] = DryingMachine(
                process_name=f"drying_{electrode_type}",
                drying_parameters=default_drying_parameters,
                event_bus=self.__event_bus,
            )
            self.__factory_structure[electrode_type]["calendaring"] = (
                CalendaringMachine(
                    process_name=f"calendaring_{electrode_type}",
                    calendaring_parameters=default_calendaring_parameters,
                    event_bus=self.__event_bus,
                )
            )
            self.__factory_structure[electrode_type]["slitting"] = SlittingMachine(
                process_name=f"slitting_{electrode_type}",
                slitting_parameters=default_slitting_parameters,
                event_bus=self.__event_bus,
            )
            self.__factory_structure[electrode_type]["inspection"] = (
                ElectrodeInspectionMachine(
                    process_name=f"inspection_{electrode_type}",
                    electrode_inspection_parameters=default_electrode_inspection_parameters,
                    event_bus=self.__event_bus,
                )
            )
        # Create and append cell line machines
        self.__factory_structure["cell"]["rewinding"] = RewindingMachine(
            process_name="rewinding_cell",
            rewinding_parameters=default_rewinding_parameters,
            event_bus=self.__event_bus,
        )
        self.__factory_structure["cell"]["electrolyte_filling"] = (
            ElectrolyteFillingMachine(
                process_name="electrolyte_filling_cell",
                electrolyte_filling_parameters=default_electrolyte_filling_parameters,
                event_bus=self.__event_bus,
            )
        )
        self.__factory_structure["cell"]["formation_cycling"] = FormationCyclingMachine(
            process_name="formation_cycling_cell",
            formation_cycling_parameters=default_formation_cycling_parameters,
            event_bus=self.__event_bus,
        )
        self.__factory_structure["cell"]["aging"] = AgingMachine(
            process_name="aging_cell",
            aging_parameters=default_aging_parameters,
            event_bus=self.__event_bus,
        )

    def __attach_batch_context(self, event: PlantSimulationEvent):
        """Include batch information on machine events before dispatch."""
        # If event already has batch_id or no data, skip
        if not event.data or "batch_id" in event.data:
            return
        # should have the machine_id
        if not "machine_id" in event.data:
            raise
        # obtain the batch_id from the running machine
        batch_id_from_machine_batch_list = self.__machine_batch_context[
            event.data["machine_id"]
        ]
        event.data["batch_id"] = batch_id_from_machine_batch_list

    def __get_machine(self, line_type: str, machine_id: str):
        """gets the machine at a particular line, throws if none exists"""
        if line_type not in self.__factory_structure:
            raise ValueError(f"Line type '{line_type}' is not found")
        elif machine_id not in self.__factory_structure[line_type]:
            raise ValueError(f"Machine '{machine_id}' is not found")
        else:
            return self.__factory_structure[line_type][machine_id]

    def __get_machine_lock(self, line_type: str, machine_id: str):
        if line_type not in self.__factory_structure:
            raise ValueError(f"Line type '{line_type}' is not found")
        elif machine_id not in self.__factory_structure[line_type]:
            raise ValueError(f"Machine '{machine_id}' is not found")
        else:
            return self.__machine_lock_structure[line_type][machine_id]

    def __run_batch_on_machines(
        self,
        line_type: str,
        batch: Batch,
        machine_list: Optional[list[str]],
    ):
        """runs the batch across a number of machines, fails
        if the machine is not found or the machine list is not in the correct order"""
        model = batch.get_batch_model(line_type)
        for machine_id in machine_list:
            running_machine = self.__get_machine(line_type, machine_id)
            machine_lock = self.__get_machine_lock(line_type, machine_id)
            with machine_lock:
                # attach batch information into machine-batch context
                machine_name = running_machine.process_name
                self.__machine_batch_context[machine_name] = (
                    batch.batch_id
                )  # attach the current batch id associated with the machine
                try:
                    running_machine.receive_model_from_previous_process(model)
                    running_machine.run_simulation(verbose=False)
                finally:
                    # remove batch information from machine-batch context
                    self.__machine_batch_context.pop(machine_name, None)
                model = running_machine.empty_model()
                batch.update_batch_model(line_type, model)

    def __run_pipeline_on_batch(self, batch: Batch, verbose: bool = False):
        """
        wraps the initial notification phase in the condition so that the subsequent notify_all() is legal
        (Python requires the condition to be held when calling notify_all).
        This wake-up lets any batch thread waiting in the queue re-check availability as soon as mixing finishes.
        """

        def __notify_start_batch_processing(batch, verbose):
            # Batch started processing
            if verbose:
                print(
                    f"EMIT EVENT - BATCH_STARTED_PROCESSING: Batch processing started for batch {batch.batch_id}."
                )
            # emit batch started processing event
            self.__event_bus.emit_plant_simulation_event(
                PlantSimulationEventType.BATCH_STARTED_PROCESSING,
                {"batch_id": batch.batch_id},
            )

        # NOTICE NOTICE NOTICE: CONDITION VARIABLE CHANGED HERE!
        def __run_mixing_stages_on_batch(batch, verbose):
            stages_to_run = ["mixing"]
            # threads for concurrent-like simulation
            run_anode_mixing_thread = Thread(
                target=self.__run_batch_on_machines,
                args=(
                    "anode",
                    batch,
                    stages_to_run,
                ),
            )
            run_cathode_mixing_thread = Thread(
                target=self.__run_batch_on_machines,
                args=(
                    "cathode",
                    batch,
                    stages_to_run,
                ),
            )
            # Batch started processing anode
            if verbose:
                print(
                    f"EMIT EVENT - BATCH_STARTED_ANODE_LINE: Anode processing started for batch {batch.batch_id}."
                )
            # start anode thread
            run_anode_mixing_thread.start()
            # emit batch started processing anode event
            self.__event_bus.emit_plant_simulation_event(
                PlantSimulationEventType.BATCH_STARTED_ANODE_LINE,
                {"batch_id": batch.batch_id},
            )
            # Batch started processing cathode
            if verbose:
                print(
                    f"EMIT EVENT - BATCH_STARTED_CATHODE_LINE: Cathode processing started for batch {batch.batch_id}. Emitting event."
                )
            # start cathode thread
            run_cathode_mixing_thread.start()
            # emit batch started processing cathode event
            self.__event_bus.emit_plant_simulation_event(
                PlantSimulationEventType.BATCH_STARTED_CATHODE_LINE,
                {"batch_id": batch.batch_id},
            )
            # Wait for anode & cathode processing finish
            run_anode_mixing_thread.join()
            if verbose:
                print(
                    f"NO EMIT: Anode mixing processing finished for batch {batch.batch_id}."
                )
            # no emit as still in anode processing
            run_cathode_mixing_thread.join()
            if verbose:
                print(
                    f"NO EMIT: Cathode mixing processing finished for batch {batch.batch_id}."
                )
            # no emit as still in anode processing
            # This is necessary to allow other thread to be executed straight away when mixing machines are available
            with self.__access_pipeline_condition:
                self.__pipeline_is_ready = True
                self.__access_pipeline_condition.notify_all()

        def __run_remaining_stages_of_electrode_lines_on_batch(
            batch: Batch, verbose: bool
        ):
            # Continue with the remaining electrode line stages in parallel
            stages_to_run = [
                "coating",
                "drying",
                "calendaring",
                "slitting",
                "inspection",
            ]
            # create threads for concurrent anode-cathode simulation
            run_anode_thread = Thread(
                target=self.__run_batch_on_machines,
                args=("anode", batch, stages_to_run),
            )
            run_cathode_thread = Thread(
                target=self.__run_batch_on_machines,
                args=("cathode", batch, stages_to_run),
            )
            # run the remaining stages
            run_anode_thread.start()
            run_cathode_thread.start()
            # finish anode processing
            run_anode_thread.join()
            # logging
            if verbose:
                print(
                    f"EMIT EVENT - BATCH_COMPLETED_ANODE_LINE: Anode processing done for batch {batch.batch_id}."
                )
            # emit event - finish anode processing
            self.__event_bus.emit_plant_simulation_event(
                PlantSimulationEventType.BATCH_COMPLETED_ANODE_LINE,
                {"batch_id": batch.batch_id},
            )
            run_cathode_thread.join()
            # logging
            if verbose:
                print(
                    f"EMIT EVENT - BATCH_COMPLETED_CATHODE_LINE: Cathode processing done for batch {batch.batch_id}."
                )
            # emit event - finish cathode processing
            self.__event_bus.emit_plant_simulation_event(
                PlantSimulationEventType.BATCH_COMPLETED_CATHODE_LINE,
                {"batch_id": batch.batch_id},
            )

        def __assemble_batch_to_cell(batch, verbose):
            # assemble anode-cathode
            batch.assemble_cell_line_model()
            if verbose:
                print(
                    f"EMIT EVENT - BATCH_ASSEMBLED: Assembled cell for batch {batch.batch_id}."
                )
            # emit event - batch assembled to cell
            self.__event_bus.emit_plant_simulation_event(
                PlantSimulationEventType.BATCH_ASSEMBLED, {"batch_id": batch.batch_id}
            )

        def __run_cell_line_on_batch(batch, verbose):
            stages_to_run = [
                "rewinding",
                "electrolyte_filling",
                "formation_cycling",
                "aging",
            ]
            # Batch started processing cell line
            if verbose:
                print(
                    f"EMIT EVENT - BATCH_STARTED_CELL_LINE: Cell processing started for batch {batch.batch_id}"
                )
            # emit event - start cell processing
            self.__event_bus.emit_plant_simulation_event(
                PlantSimulationEventType.BATCH_STARTED_CELL_LINE,
                {"batch_id": batch.batch_id},
            )
            self.__run_batch_on_machines("cell", batch, stages_to_run)
            # Batch finished processing cell line
            if verbose:
                print(
                    f"EMIT EVENT - BATCH_COMPLETED_CELL_LINE: Cell processing finished for batch {batch.batch_id}"
                )
            # emait event - finish cell processing
            self.__event_bus.emit_plant_simulation_event(
                PlantSimulationEventType.BATCH_COMPLETED_CELL_LINE,
                {"batch_id": batch.batch_id},
            )

        def __notify_finish__batch__processing(batch, verbose):
            # Batch finished whole pipeline
            if verbose:
                print(
                    f"EMIT EVENT - BATCH_COMPLETED: Finished pipeline processing for batch {batch.batch_id}"
                )
            # Emit event - finish batch processing
            self.__event_bus.emit_plant_simulation_event(
                PlantSimulationEventType.BATCH_COMPLETED, {"batch_id": batch.batch_id}
            )

        """
        INFO: Main simulation logic here!!!
        """
        __notify_start_batch_processing(batch, verbose)
        __run_mixing_stages_on_batch(batch, verbose)
        __run_remaining_stages_of_electrode_lines_on_batch(batch, verbose)
        __assemble_batch_to_cell(batch, verbose)
        __run_cell_line_on_batch(batch, verbose)
        __notify_finish__batch__processing(batch, verbose)
        return True

    def __process_batch_request(self, batch: Batch, verbose: bool = False):
        """
        An internal operation of a worker thread for one batch.
        Efficiently check for the availability of the mixing machines and whether it is at the start of the queue.
        Then executes the pipeline operation and removes itself from the queue.
        """
        # acquire the condition's lock because of access to the list
        while True:
            with self.__access_pipeline_condition:
                # if the batch is the start of the queue
                batch_is_at_front = (
                    self.__batch_request_list[0].batch_id == batch.batch_id
                )
                if batch_is_at_front and self.__pipeline_is_ready:
                    # get the first batch in the queue
                    self.__batch_request_list.pop(0)
                    # append it to the running batches
                    self.__running_batch_list.append(batch)
                    # set the pipeline state to busy (mostly about the mixing machines being busy)
                    self.__pipeline_is_ready = False
                    break
                else:
                    # else: tell the thread to wait
                    self.__access_pipeline_condition.wait()
        try:
            # start simulation
            self.__run_pipeline_on_batch(batch, verbose=verbose)
        finally:
            # access queue/list
            with self.__access_pipeline_condition:
                if batch in self.__running_batch_list:
                    self.__running_batch_list.remove(batch)
                self.__batch_worker_thread_list.pop(batch.batch_id, None)
                # notify that a batch has been finished to the other parked threads
                # this is necessary for the other thread to be processed. The parked thread will execute the check again
                # self.__pipeline_condition.notify_all()

    def __maintain_monitoring_thread(self):
        """Ensure the background processing loop is running."""
        # first obtain the lock for access to the monitoring thread
        # the lock is initialised with the plant simulation object's initialisation
        with self.__runner_thread_lock:
            # indicates there should be a processing batch request
            if self.__plant_is_idle_event.is_set:
                self.__plant_is_idle_event.clear()
            # if there is no active monitoring thread OR
            # there hasn't been any monitoring thread
            if self.__runner_thread is None or not self.__runner_thread.is_alive():
                # create a monitoring thread
                self.__runner_thread = Thread(
                    target=self.__monitoring_loop,
                    name="PlantSimulationRunner",
                    daemon=True,
                )
                self.__runner_thread.start()
                # debug
                # print("There is a monitoring thread creating")
            # otherwise, just know that there is a running thread
            else:
                # debug
                # print("There is a monitoring thread running")
                pass

    def __monitoring_loop(self, poll_interval: float = 0.5):
        """
            This loop ensures and maintains that any simulation running can be still running with along with this thread.
            It also updates the event flag when there is no simulation left.
        """
        try:
            # start the loop
            while True:
                with self.__access_pipeline_condition:
                    # when there are no requests, no running batches, no processing threads
                    if (
                        not self.__batch_request_list
                        and not self.__running_batch_list
                        and not self.__batch_worker_thread_list
                    ):
                        break
                    self.__access_pipeline_condition.wait(timeout=poll_interval)
        finally:
            # if there is no more processing, and this monitoring thread senses it.
            # set the plant_is_idle flag to true
            self.__plant_is_idle_event.set()
            with self.__runner_thread_lock:
                self.__runner_thread = None

    def add_batch(self, batch: Batch = None, verbose: bool = False):
        """
        Adds a new batch to the plant simulation (maximum number of threads is 3).
        This method performs the queue mutation under the same condition lock so no worker can read a half-updated queue.
        Returns the identifier of the queued batch so callers can track it.
        """
        # make sure batch_requests, batch_worker_threads are only accessed atomically
        # wait to obtain the lock to access the simulation pipeline
        with self.__access_pipeline_condition:
            # For testing only
            if batch is None:
                # FOR TESTING ONLY
                batch = Batch(batch_id=str(self.auto_generated_batch_id))
                # FOR TESTING ONLY
                self.auto_generated_batch_id += 1

            # only allows maximum 3 batches/threads at a time
            if len(self.__batch_request_list) == 3:
                raise ValueError("Maximum number of batches reached")
            # add batch (information to the list)
            self.__batch_request_list.append(batch)

            # wraps batch processing into a thread
            batch_processing_worker = Thread(
                target=self.__process_batch_request,
                args=(batch, verbose),
                name=f"PlantBatchWorker-{batch.batch_id}",
            )
            # save batch processing thread to the thread list
            self.__batch_worker_thread_list[batch.batch_id] = batch_processing_worker

            if verbose:
                print(
                    f"EMIT EVENT - BATCH_REQUESTED: Batch id: {batch.batch_id} has arrived."
                )

            # emit event - batch requested
            self.__event_bus.emit_plant_simulation_event(
                PlantSimulationEventType.BATCH_REQUESTED,
                {
                    "batch_id": batch.batch_id,
                    "message": f"Batch id {batch.batch_id} has been requested and added to the processing queue.",
                },
            )

            # notify all the batch processing threads (needs more testing)
            # self.__access_pipeline_condition.notify_all()

        # start the batch processing request
        batch_processing_worker.start()

        # ensure the background processing loop is active
        self.__maintain_monitoring_thread()

        return batch.batch_id

    def get_machine_status(self, line_type: str, machine_id: str):
        """Due to the real-time nature of this functionality, obtaining a lock is not needed!"""
        machine = self.__get_machine(line_type, machine_id)
        return machine.get_current_state()

    def get_current_plant_state(self):
        """maybe for reporting functionalities"""
        # obtain access to the pipeline infomation first
        with self.__access_pipeline_condition:
            batch_request_list_info = [
                batch.get_batch_state() for batch in self.__batch_request_list
            ]
            running_batches = [
                batch.get_batch_state() for batch in self.__running_batch_list
            ]
            machine_statuses = [
                self.__factory_structure[line_type][machine_id].get_current_state()
                for line_type in self.__factory_structure
                for machine_id in self.__factory_structure[line_type]
            ]

        return {
            "batch_requests": batch_request_list_info,
            "running_batches": running_batches,
            "machine_statuses": machine_statuses,
        }

    def reset_plant(self):
        if not self.wait_until_plant_simulation_is_idle(timeout=5):
            raise TimeoutError(
                "Cannot reset plant. Possibly because there are simulations still running."
            )

        self.__factory_structure = {
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
        # reset the machine locks
        self.__machine_lock_structure = None
        self.__machine_lock_structure = {
            line_type: {stage: Lock() for stage in self.__factory_structure[line_type]}
            for line_type in self.__factory_structure
        }
        # empty the batch-related software memory
        with self.__access_pipeline_condition:
            self.__batch_request_list = []
            self.__running_batch_list = []
            self.__batch_worker_thread_list = {}
            self.__machine_batch_context = {}  # Clear machine batch context on reset

    def update_machine_parameters(self, line_type: str, machine_id: str, parameters):
        """Update parameters for a specific machine."""
        machine_lock = self.__get_machine_lock(line_type, machine_id)
        if machine_lock.acquire(timeout=5):
            machine = self.__get_machine(line_type, machine_id)
            machine.validate_parameters(parameters)
            machine.update_machine_parameters(parameters)
            machine_lock.release()
            return True
        else:
            raise TimeoutError(
                "Cannot update machine parameters. Possibly because this machine is busy. Please update the parameters later."
            )

    def subscribe_to_event(
        self,
        event_type: PlantSimulationEventType,
        callback: Callable[[PlantSimulationEvent], None],
        *,  # Keyword-only arguments
        include_batch_context: bool = False,
    ):
        """Expose event subscription with optional batch context enrichment."""
        if include_batch_context:

            def __callback_with_batch(event: PlantSimulationEvent):
                self.__attach_batch_context(event)
                callback(event)

            self.__event_bus.subscribe(event_type, __callback_with_batch)
        else:
            self.__event_bus.subscribe(event_type, callback)

    def wait_until_plant_simulation_is_idle(
        self, timeout: Optional[float] = None
    ) -> bool:
        """Block until the plant has finished processing all batch simulation/processing."""
        return self.__plant_is_idle_event.wait(timeout=timeout)
