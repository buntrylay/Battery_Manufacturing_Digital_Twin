from simulation.machine.BaseMachine import BaseMachine
from simulation.process_parameters.Parameters import AgingParameters
from simulation.battery_model.AgingModel import AgingModel
from simulation.battery_model.FormationCyclingModel import FormationCyclingModel

try:
    from server.notification_queue import notify_machine_status
except ImportError:
    def notify_machine_status(*args, **kwargs):
        print(f"AgingMachine Notification: {args}")
        pass


class AgingMachine(BaseMachine):
    def __init__(self, process_name: str,
                 aging_parameters: AgingParameters,
                 aging_model: AgingModel = None,
                 connection_string=None):
        super().__init__(process_name, aging_model, aging_parameters)

    def receive_model_from_previous_process(self, previous_model: FormationCyclingModel):
        self.battery_model = AgingModel(previous_model)

    def calculate_total_steps(self):
        if self.battery_model is not None and self.machine_parameters is not None:
            # 1 step = 1h
            self.total_steps = int(self.machine_parameters.aging_time_days * 24)

    def step_logic(self, t: int):
        seconds_elapsed = t * 3600
        self.battery_model.update_properties(self.machine_parameters, seconds_elapsed)

        # Start
        if t == 0:
            # notify_machine_status(
            #     machine_id=self.process_name,
            #     line_type=self.process_name.split('_')[-1],
            #     process_name=self.process_name,
            #     status="aging_started",
            #     data={
            #         "message": f"Starting {self.process_name} aging process",
            #         "aging_time_days": self.machine_parameters.aging_time_days,
            #         "temperature": self.machine_parameters.temperature
            #     }
            # )
            pass

        # Progress
        if (t % 24 == 0 and t > 0) or (t == self.total_steps - 1):
            days_elapsed = t / 24
            progress = (t / self.total_steps) * 100
            # notify_machine_status(
            #     machine_id=self.process_name,
            #     line_type=self.process_name.split('_')[-1],
            #     process_name=self.process_name,
            #     status="aging_progress",
            #     data={
            #         "message": f"Aging progress: {progress:.1f}% ({days_elapsed:.1f} days elapsed)",
            #         "days_elapsed": days_elapsed,
            #         "step": t,
            #         "total_steps": self.total_steps,
            #         "progress_percent": progress
            #     }
            # )

        # Completed
        if t == self.total_steps - 1:
            # notify_machine_status(
            #     machine_id=self.process_name,
            #     line_type=self.process_name.split('_')[-1],
            #     process_name=self.process_name,
            #     status="aging_completed",
            #     data={
            #         "message": f"🎉 COMPLETE: {self.process_name} aging completed!",
            #         "aging_time_completed": self.machine_parameters.aging_time_days,
            #         "final_state": self.get_current_state(),  # careful: có thể rất to
            #         "manufacturing_complete": True
            #     }
            # )
            pass

    def validate_parameters(self, parameters: dict):
        return AgingParameters(**parameters).validate_parameters()
