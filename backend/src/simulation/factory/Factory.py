import threading
from typing import List, Dict
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
        Wait for all dependencies to complete
        """
        for dependency_id in machine.dependencies:
            print(f"Waiting for dependency: {dependency_id} to be completed")
            self.machine_events[dependency_id].wait()
            print(f"Dependency: {dependency_id} has been completed")

        if "coating_machine" in machine.dependencies:
            print("Coating machine is dependent on the mixing machines")
            time.sleep(10) # 10 second delay
            print("Coating machine is now ready to start")
    
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
                daemon=True
            )
            thread.start()
            self.threads.append(thread)

    def stop_simulation(self):
        """
        Stop all running machines.
        """
        self.is_running = False
        for thread in self.threads:
            thread.join()
        print("Factory simulation stopped.") 