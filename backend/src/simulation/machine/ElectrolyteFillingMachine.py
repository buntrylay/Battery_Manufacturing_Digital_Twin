import os
import json
import time
import threading
from datetime import datetime, timedelta
from simulation.machine.BaseMachine import BaseMachine
from simulation.sensor.ElectrolyteFillingProcess import ElectrolyteFillingCalculation


class ElectrolyteFillingMachine(BaseMachine):
    
    def _init_(self, id, machine_parameter: dict):
        super().__init__(id)
        self.name = "ElectrolyteFillingMachine"
        self.start_datatime= datetime.now()
        self.total_time = 0
        self.lock = threading.Lock()
        
        
        self.output_dir = os.path.join(os.getcwd(), "filling_out")
        os.makedirs(self.output_dir, exist_ok = True)
        print(f"Output directory created at: {self.output_dir}")
        
        self.P_vac = machine_parameter["Vaccuum Level"]
        self.P_fill = machine_parameter["Vaccum Filling"]
        self.T_soak = machine_parameter["Soaking time"]
        
        self.phi_final = None
        
        self.calculator = ElectrolyteFillingCalculation()
        
        
    def update_from_rewind(self, rewind_data):
        with self.lock:
            "phi_final" = rewind_data.get("phi_final") #push the phi from Calendaring"
            print()