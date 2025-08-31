from simulation.machine.BaseMachine import BaseMachine

class DryingMachine(BaseMachine):
    def __init__(self, drying_model, drying_parameters):
        super().__init__("Drying", drying_model, drying_parameters)

    def run(self):
        self.turn_on()
        all_results = []
        total_steps = self.battery_model.time_steps(self.machine_parameters)

        for t in range(total_steps):
            self.total_time = t
            proc = self.battery_model.update_properties(self.machine_parameters)
            result = self.get_current_properties(process_specifics=proc)
            all_results.append(result)
            self.save_data_to_local_folder()

        self.save_all_results(all_results)
        self.turn_off()

    def get_output(self):
        """Feed sang Calendaring stage"""
        return {
            "dry_thickness": self.battery_model.dry_thickness,
            "solid_content": self.battery_model.solid_content,
            "defect_risk": self.battery_model.defect_risk
        }
