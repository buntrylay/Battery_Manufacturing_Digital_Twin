import threading
from typing import List, Dict
from simulation.machine.MixingMachine import MixingMachine
from simulation.machine.CoatingMachine import CoatingMachine
from simulation.machine.CalendaringMachine import CalendaringMachine
from simulation.machine.DryingMachine import DryingMachine
from simulation.machine.SlittingMachine import SlittingMachine
from simulation.machine.ElectrodeInspectionMachine import ElectrodeInspectionMachine
from simulation.machine.RewindingMachine import RewindingMachine
from simulation.machine.ElectrolyteFillingMachine import ElectrolyteFillingMachine
from simulation.machine.FomationCyclingMachine import FormationCyclingMachine
from simulation.machine.AgingMachine import AgingMachine

import time

"""
Factory class that simulates a factory with multiple machines.
Handles machines being able to run in parallel.
Will similar to a real life factory that has different production lines.
"""

class Factory:
    def __init__(self):
        """
        Initialize factory with an empty list of machine and tread tracking. 
        args:
            self.threads[] handles the number of threads running
            self.is_running is a boolean check for the current factory state
            self.machine_status creates a dictionary that tracks each machines completion status
            self.machine_locks creates a dictionary that tracks each machines lock status updates
            self.machine_events creates a dictionary that tracks each machines completion signal
        """
        self.machines = []
        self.threads = []
        self.is_running = False
        self.machine_status = {}
        self.machine_locks = {}
        self.machine_events = {}
        self.shutdown_event = threading.Event()

    def add_machine(self, machine, dependencies=None):
        """
        Add a machine to the factory with optional dependencies.
        
        Args:
            machine: Is the machine to add
            dependencies: List of machine IDs that must complete before this machine starts
        """
        self.machines.append(machine)
        self.machine_status[machine.id] = False
        self.machine_locks[machine.id] = threading.Lock()
        self.machine_events[machine.id] = threading.Event()
        if dependencies:
            machine.dependencies = dependencies
        else:
            machine.dependencies = []

    def wait_for_dependencies(self, machine):
        """
        Wait for all dependencies to complete and pass their outputs if needed.
        """
        for dependency_id in machine.dependencies:
            print(f"[{machine.id}] Waiting for dependency: {dependency_id} to complete...")
            self.machine_events[dependency_id].wait()
            print(f"[{machine.id}] Dependency {dependency_id} has been completed.")

            # Get the machine instance for the dependency
            dependency_machine = next((m for m in self.machines if m.id == dependency_id), None)
            if not dependency_machine:
                print(f"[{machine.id}] Error: Dependency machine {dependency_id} not found.")
                continue

            # Mixing → Coating
            if isinstance(dependency_machine, MixingMachine) and isinstance(machine, CoatingMachine):
                final_slurry = dependency_machine.get_final_slurry()
                print(f"[{machine.id}] Receiving slurry from {dependency_id}")
                machine.update_from_slurry(final_slurry)

            # Coating → Drying
            if isinstance(dependency_machine, CoatingMachine) and isinstance(machine, DryingMachine):
                wet_thickness, solid_content = dependency_machine.get_final_coating()
                print(f"[{machine.id}] Receiving coated data from {dependency_id}")
                machine.update_from_coating(wet_thickness, solid_content)

            # Drying → Calendaring
            if isinstance(dependency_machine, DryingMachine) and isinstance(machine, CalendaringMachine):
                dry_thickness = dependency_machine.get_final_drying()
                print(f"[{machine.id}] Receiving dried data from {dependency_id}")
                machine.update_from_drying(dry_thickness)

            # Calendaring → Slitting
            if isinstance(dependency_machine, CalendaringMachine) and isinstance(machine, SlittingMachine):
                cal_data = dependency_machine.get_final_calendaring()
                print(f"[{machine.id}] Receiving calendaring data from {dependency_id}")
                machine.update_from_calendaring(cal_data)
            
            # Slitting -> Electrode Inspection
            if isinstance(dependency_machine, SlittingMachine) and isinstance(machine, ElectrodeInspectionMachine):
                slitting_data = dependency_machine.get_final_slitting()
                print(f"[{machine.id}] Receiving slitting data from {dependency_id}")
                machine.update_from_slitting(slitting_data)
                
            # Electrode Inspection -> Rewinding
            if isinstance(dependency_machine, ElectrodeInspectionMachine) and isinstance(machine, RewindingMachine):
                inspection_data = dependency_machine.get_final_inspection()
                print(f"[{machine.id}] Receiving inspection data from {dependency_id}")
                machine.update_from_inspection(inspection_data)
                
            # Rewinding -> Electrolyte Filling
            if isinstance(dependency_machine, RewindingMachine) and isinstance(machine, ElectrolyteFillingMachine):
                rewind_data = dependency_machine.get_final_rewind()
                print(f"[{machine.id}] Receiving inspection data from {dependency_id}")
                machine.update_from_rewind(rewind_data)

            #Electrode Filling -> Formation Cycling
            if isinstance(dependency_machine, ElectrolyteFillingMachine) and isinstance(machine, FormationCyclingMachine):
                filling_data = dependency_machine.get_final_filling()
                print(f"[{machine.id}] Receiving filling data from {dependency_id}")
                machine.update_from_filling(filling_data)
                
            # # Formation Cycling -> Aging
            if isinstance(dependency_machine, FormationCyclingMachine) and isinstance(machine, AgingMachine):
                formation_data = dependency_machine.get_final_formation_properties()
                print(f"[{machine.id}] Receiving formation data from {dependency_id}")
                machine.update_from_formation_cycling(formation_data)

    def run_machine(self, machine):
        """
         Run a single machine within its own thread, handling dependencies.
        """
        try:
            # Wait for dependencies if any
            if hasattr(machine, 'dependencies') and machine.dependencies:
                self.wait_for_dependencies(machine)

            print(f"Starting {machine.id}...")
            machine.turn_on()
            machine.run()
            machine.turn_off()
            
            # Mark machine as complete
            with self.machine_locks[machine.id]:
                self.machine_status[machine.id] = True
                self.machine_events[machine.id].set()  # Signal completion
            
            print(f"Completed {machine.id}")
        except Exception as e:
            print(f"Error in {machine.id}: {str(e)}")
        finally:
            # Ensure the event is set even if there's an error
            self.machine_events[machine.id].set()

    def start_simulation(self):
        """
        Start the simulation
        """
        self.is_running = True
        print("Starting factory simulation...")

        for machine in self.machines:
            thread = threading.Thread(
                target=self.run_machine,
                args=(machine,),
                daemon=False  # Make threads non-daemon
            )
            thread.start()
            self.threads.append(thread)

    def stop_simulation(self):
        """
        Stop all running machines and wait for threads to complete.
        """
        self.is_running = False
        self.shutdown_event.set()
        
        # Wait for all threads to complete
        for thread in self.threads:
            thread.join(timeout=5.0)  # Wait up to 5 seconds for each thread
        
        # Clear all events
        for event in self.machine_events.values():
            event.set()
            
        print("Factory simulation stopped.")

    def __del__(self):
        """
        Cleanup when the factory is destroyed.
        """
        self.stop_simulation() 