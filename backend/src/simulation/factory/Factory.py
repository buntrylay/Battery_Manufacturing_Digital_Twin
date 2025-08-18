import threading
from typing import List, Dict, Tuple
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
New Factory class that implements a pipeline-based approach:
1. Anode and Cathode lines run concurrently for mixing, coating, and calendaring
2. After calendaring, the two lines merge into a single production line
3. Subsequent processes (slitting, inspection, etc.) run sequentially on the merged line
4. No dependency checking - just straightforward pipeline flow
"""
""" How about using a dataclass to store the production lines? Brainstorming...
# @dataclass
# class Factory:
#     anode_production_line: {
#         'mixing': MixingMachine,
#         'coating': CoatingMachine,
#         'drying': DryingMachine,
#         'calendaring': CalendaringMachine
#     }
#     cathode_production_line: {
#         'mixing': MixingMachine,
#         'coating': CoatingMachine,
#         'drying': DryingMachine,
#         'calendaring': CalendaringMachine
#     }
#     merged_line: {
#         'slitting': SlittingMachine,
#         'inspection': ElectrodeInspectionMachine,
#         'rewinding': RewindingMachine,
#         'electrolyte_filling': ElectrolyteFillingMachine,
#         'formation_cycling': FormationCyclingMachine,
#         'aging': AgingMachine
#     }
"""

class Factory:
    def __init__(self):
        """
        Initialize factory with pipeline structure.
        """
        # This is a flag to check if the simulation is running.
        self.is_running = False

        self.shutdown_event = threading.Event()
        
        # Separate anode and cathode lines for concurrent processing. 
        # This is a dictionary of machines.
        self.anode_production_line = {
            'mixing': None,
            'coating': None,
            'drying': None,
            'calendaring': None
        }
        
        self.cathode_production_line = {
            'mixing': None,
            'coating': None,
            'drying': None,
            'calendaring': None
        }
        
        # Merged production line for sequential processing
        self.merged_line = {
            'slitting': None,
            'inspection': None,
            'rewinding': None,
            'electrolyte_filling': None,
            'formation_cycling': None,
            'aging': None
        }

    # could be cleaner...
    # more type safety, less magic strings, etc.
    # can use try/catch to handle the type errors (if the machine is not a valid one for the position)
    def add_machine(self, machine, line_type: str, position: str):
        """
        Add a machine to the appropriate production line.
        
        Args:
            machine: The machine to add
            line_type: Either 'anode', 'cathode', or 'merged'
            position: The position in the line (e.g., 'mixing', 'coating', etc.)
        """
        if line_type == 'anode':
            if position in self.anode_production_line:
                self.anode_production_line[position] = machine
            else:
                raise ValueError(f"Invalid anode line position: {position}")
        elif line_type == 'cathode':
            if position in self.cathode_production_line:
                self.cathode_production_line[position] = machine
            else:
                raise ValueError(f"Invalid cathode line position: {position}")
        elif line_type == 'merged':
            if position in self.merged_line:
                self.merged_line[position] = machine
            else:
                raise ValueError(f"Invalid merged line position: {position}")
        else:
            raise ValueError(f"Invalid line type: {line_type}")

    # run_anode_line and run_cathode_line could be encapsulated into a single function
    # that takes a line_type, process_input as an argument
    # but previously the machines, although they are all BaseMachine, have different methods. 
    # therefore, we need to standardise the methods in the BaseMachine class.
    # it could be run_production_line(self, line_type: str, process_input: dict)
    def run_anode_line(self):
        """
        Run the anode production line: mixing → coating → drying → calendaring
        """
        print("Starting Anode Production Line...")
        
        # Mixing
        if self.anode_production_line['mixing']:
            print(f"Running {self.anode_production_line['mixing'].id}...")
            self.anode_production_line['mixing'].turn_on()
            self.anode_production_line['mixing'].run()
            anode_slurry = self.anode_production_line['mixing'].get_final_slurry()
            self.anode_production_line['mixing'].turn_off()
            print(f"Anode mixing completed. Slurry: {anode_slurry}")
        
        # Coating
        if self.anode_production_line['coating']:
            print(f"Running {self.anode_production_line['coating'].id}...")
            self.anode_production_line['coating'].turn_on()
            if anode_slurry:
                self.anode_production_line['coating'].update_from_slurry(anode_slurry)
            self.anode_production_line['coating'].run()
            anode_coating_data = self.anode_production_line['coating'].get_final_coating()
            self.anode_production_line['coating'].turn_off()
            print(f"Anode coating completed. Data: {anode_coating_data}")
        
        # Drying
        if self.anode_production_line['drying']:
            print(f"Running {self.anode_production_line['drying'].id}...")
            self.anode_production_line['drying'].turn_on()
            if anode_coating_data:
                self.anode_production_line['drying'].update_from_coating(*anode_coating_data)
            self.anode_production_line['drying'].run()
            anode_drying_data = self.anode_production_line['drying'].get_final_drying()
            self.anode_production_line['drying'].turn_off()
            print(f"Anode drying completed. Data: {anode_drying_data}")
        
        # Calendaring
        if self.anode_production_line['calendaring']:
            print(f"Running {self.anode_production_line['calendaring'].id}...")
            self.anode_production_line['calendaring'].turn_on()
            if anode_drying_data:
                self.anode_production_line['calendaring'].update_from_drying(anode_drying_data)
            self.anode_production_line['calendaring'].run()
            anode_calendaring_data = self.anode_production_line['calendaring'].get_final_calendaring()
            self.anode_production_line['calendaring'].turn_off()
            print(f"Anode calendaring completed. Data: {anode_calendaring_data}")
        
        print("Anode Production Line completed!")
        return anode_calendaring_data

    def run_cathode_line(self):
        """
        Run the cathode production line: mixing → coating → drying → calendaring
        """
        print("Starting Cathode Production Line...")
        
        # Mixing
        if self.cathode_production_line['mixing']:
            print(f"Running {self.cathode_production_line['mixing'].id}...")
            self.cathode_production_line['mixing'].turn_on()
            self.cathode_production_line['mixing'].run()
            cathode_slurry = self.cathode_production_line['mixing'].get_final_slurry()
            self.cathode_production_line['mixing'].turn_off()
            print(f"Cathode mixing completed. Slurry: {cathode_slurry}")
        
        # Coating
        if self.cathode_production_line['coating']:
            print(f"Running {self.cathode_production_line['coating'].id}...")
            self.cathode_production_line['coating'].turn_on()
            if cathode_slurry:
                self.cathode_production_line['coating'].update_from_slurry(cathode_slurry)
            self.cathode_production_line['coating'].run()
            cathode_coating_data = self.cathode_production_line['coating'].get_final_coating()
            self.cathode_production_line['coating'].turn_off()
            print(f"Cathode coating completed. Data: {cathode_coating_data}")
        
        # Drying
        if self.cathode_production_line['drying']:
            print(f"Running {self.cathode_production_line['drying'].id}...")
            self.cathode_production_line['drying'].turn_on()
            if cathode_coating_data:
                self.cathode_production_line['drying'].update_from_coating(*cathode_coating_data)
            self.cathode_production_line['drying'].run()
            cathode_drying_data = self.cathode_production_line['drying'].get_final_drying()
            self.cathode_production_line['drying'].turn_off()
            print(f"Cathode drying completed. Data: {cathode_drying_data}")
        
        # Calendaring
        if self.cathode_production_line['calendaring']:
            print(f"Running {self.cathode_production_line['calendaring'].id}...")
            self.cathode_production_line['calendaring'].turn_on()
            if cathode_drying_data:
                self.cathode_production_line['calendaring'].update_from_drying(cathode_drying_data)
            self.cathode_production_line['calendaring'].run()
            cathode_calendaring_data = self.cathode_production_line['calendaring'].get_final_calendaring()
            self.cathode_production_line['calendaring'].turn_off()
            print(f"Cathode calendaring completed. Data: {cathode_calendaring_data}")
        
        print("Cathode Production Line completed!")
        return cathode_calendaring_data

    def run_merged_line(self, anode_data, cathode_data):
        """
        Run the merged production line sequentially: slitting → inspection → rewinding → etc.
        """
        print("Starting Merged Production Line...")
        
        # Combine anode and cathode data for merged processing
        merged_input = {
            'anode': anode_data,
            'cathode': cathode_data
        }
        
        # Slitting
        if self.merged_line['slitting']:
            print(f"Running {self.merged_line['slitting'].id}...")
            self.merged_line['slitting'].turn_on()
            self.merged_line['slitting'].update_from_calendaring(anode_data)
            self.merged_line['slitting'].run()
            slitting_data = self.merged_line['slitting'].get_final_slitting()
            self.merged_line['slitting'].turn_off()
            print(f"Slitting completed. Data: {slitting_data}")
        
        # Electrode Inspection
        if self.merged_line['inspection']:
            print(f"Running {self.merged_line['inspection'].id}...")
            self.merged_line['inspection'].turn_on()
            if slitting_data:
                self.merged_line['inspection'].update_from_slitting(slitting_data)
            self.merged_line['inspection'].run()
            inspection_data = self.merged_line['inspection'].get_final_inspection()
            self.merged_line['inspection'].turn_off()
            print(f"Electrode inspection completed. Data: {inspection_data}")
        
        # Rewinding
        if self.merged_line['rewinding']:
            print(f"Running {self.merged_line['rewinding'].id}...")
            self.merged_line['rewinding'].turn_on()
            if inspection_data:
                self.merged_line['rewinding'].update_from_inspection(inspection_data)
            self.merged_line['rewinding'].run()
            rewinding_data = self.merged_line['rewinding'].get_final_rewind()
            self.merged_line['rewinding'].turn_off()
            print(f"Rewinding completed. Data: {rewinding_data}")
        
        # Electrolyte Filling
        if self.merged_line['electrolyte_filling']:
            print(f"Running {self.merged_line['electrolyte_filling'].id}...")
            self.merged_line['electrolyte_filling'].turn_on()
            if rewinding_data:
                self.merged_line['electrolyte_filling'].update_from_rewind(rewinding_data)
            self.merged_line['electrolyte_filling'].run()
            filling_data = self.merged_line['electrolyte_filling'].get_final_filling()
            self.merged_line['electrolyte_filling'].turn_off()
            print(f"Electrolyte filling completed. Data: {filling_data}")
        
        # Formation Cycling
        if self.merged_line['formation_cycling']:
            print(f"Running {self.merged_line['formation_cycling'].id}...")
            self.merged_line['formation_cycling'].turn_on()
            if filling_data:
                self.merged_line['formation_cycling'].update_from_filling(filling_data)
            self.merged_line['formation_cycling'].run()
            formation_data = self.merged_line['formation_cycling'].get_final_formation_properties()
            self.merged_line['formation_cycling'].turn_off()
            print(f"Formation cycling completed. Data: {formation_data}")
        
        # Aging
        if self.merged_line['aging']:
            print(f"Running {self.merged_line['aging'].id}...")
            self.merged_line['aging'].turn_on()
            if formation_data:
                self.merged_line['aging'].update_from_formation_cycling(formation_data)
            self.merged_line['aging'].run()
            aging_data = self.merged_line['aging'].get_process_properties()
            self.merged_line['aging'].turn_off()
            print(f"Aging completed. Data: {aging_data}")
        
        print("Merged Production Line completed!")
        return aging_data

    def start_simulation(self):
        """
        Start the pipeline simulation with concurrent anode/cathode lines, then merged line.
        """
        if self.is_running:
            print("Simulation is already running!")
            return
        
        self.is_running = True
        print("Starting Factory Pipeline Simulation...")
        
        try:
            # Run anode and cathode lines concurrently
            anode_thread = threading.Thread(target=self.run_anode_line, name="AnodeLine")
            cathode_thread = threading.Thread(target=self.run_cathode_line, name="CathodeLine")
            
            anode_thread.start()
            cathode_thread.start()
            
            # Wait for both lines to complete
            anode_thread.join()
            cathode_thread.join()
            
            # Get results from both lines
            anode_data = self.anode_production_line['calendaring'].get_final_calendaring() if self.anode_production_line['calendaring'] else None
            cathode_data = self.cathode_production_line['calendaring'].get_final_calendaring() if self.cathode_production_line['calendaring'] else None
            
            print("Both production lines completed. Merging for final processing...")
            
            # Run the merged line sequentially
            final_result = self.run_merged_line(anode_data, cathode_data)
            
            print("Factory Pipeline Simulation completed successfully!")
            return final_result
            
        except Exception as e:
            print(f"Error during simulation: {str(e)}")
            raise
        finally:
            self.is_running = False

    def stop_simulation(self):
        """
        Stop the simulation.
        """
        self.is_running = False
        self.shutdown_event.set()
        print("Factory simulation stopped.")

    def __del__(self):
        """
        Cleanup when the factory is destroyed.
        """
        self.stop_simulation()