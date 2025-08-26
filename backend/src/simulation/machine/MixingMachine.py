import time
import numpy as np
from simulation.machine.BaseMachine import BaseMachine
from simulation.battery_model.MixingModel import MixingModel
from dataclasses import dataclass

@dataclass
class MaterialRatios:
    AM: float
    CA: float
    PVDF: float
    solvent: float

@dataclass
class MixingParameters:
    mixing_tank_volume: float # L
    material_ratios: MaterialRatios

class MixingMachine(BaseMachine):
    """
    A machine class for simulating the mixing of battery slurry components.
 
    This class handles the stepwise addition of components to a slurry, simulates
    process parameters (temperature, pressure, RPM), and generates real-time
    simulation data in JSON format. Utility methods are used for formatting results,
    writing output files, and printing process information.
 
    Attributes:
        slurry (Slurry): The slurry being mixed.
        electrode_type (str): Type of electrode being produced ("Anode" or "Cathode").
        RHO_values (dict): Density values for different components.
        WEIGHTS_values (dict): Weight coefficients for property calculations.
        volume (float): Total volume of the slurry in litres.
        ratios (dict): Mixing ratios for different components.
        total_time (float): Total mixing time in seconds.
        calculator (SlurryPropertyCalculator): Calculator for slurry properties.
    """
   
    def __init__(self, mixing_model: MixingModel, mixing_parameters: MixingParameters, connection_string=None):
        """
        Initialise a new MixingMachine instance.
 
        Args:
            id (str): Unique identifier for the machine.
            electrode_type (str): Type of electrode ("Anode" or "Cathode").
            slurry (Slurry): The slurry object to be mixed.
            ratio_materials (dict): Dictionary containing mixing ratios for components.
        """
        super().__init__(f"Mixing_{mixing_model.electrode_type}", mixing_model, mixing_parameters, connection_string)
 
    def _mix_component(self, material_type, step_percent, pause_sec, duration_sec, results_list):
        total_volume_of_material_to_add = self.machine_parameters.mixing_tank_volume * self.machine_parameters.material_ratios[material_type]
        volume_added_in_each_step = step_percent * total_volume_of_material_to_add
        added_volume = 0.0
        comp_start_time = self.total_time
        last_saved_time = time.time()
        last_saved_result = None
        while self.total_time - comp_start_time < duration_sec:
            self.ref_temperature = np.random.normal(loc=25, scale=1)
            self.total_time += pause_sec
            if added_volume < total_volume_of_material_to_add:
                add_amt = min(volume_added_in_each_step, total_volume_of_material_to_add - added_volume)
                self.battery_model.add(material_type, add_amt)
                added_volume += add_amt
            self.battery_model.update_properties()
            result = self.get_current_properties()
            results_list.append(result)
            now = time.time()
            if now - last_saved_time >= 0.1 and result != last_saved_result:  # Check if data has changed
                # self.send_json_to_iothub(result)  # Send to IoT Hub
                self.save_data_to_local_folder()  # Print to console
                last_saved_time = now
                last_saved_result = result
            time.sleep(pause_sec)
 
    def run(self, step_percent=0.02, pause_sec=0.1):
        self.turn_on()
        all_results = []
        self._mix_component("PVDF", step_percent, pause_sec, 8, all_results)
        self._mix_component("CA", step_percent, pause_sec, 8, all_results)
        self._mix_component("AM", step_percent, pause_sec, 10, all_results)
        self.save_all_results(all_results)
        self.turn_off()
