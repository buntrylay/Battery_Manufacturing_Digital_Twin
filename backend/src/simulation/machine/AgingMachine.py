import simulation.machine.BaseMachine as BaseMachine
from dataclasses import dataclass
from simulation.process_parameters.Parameters import AgingParameters
from simulation.battery_model.AgingModel import AgingModel
from simulation.battery_model.FormationCyclingModel import FormationCyclingModel

# Import notification functions
try:
    # Try multiple import paths to handle different environments
    try:
        from server.notification_queue import notify_machine_status
    except ImportError:
        from backend.src.server.notification_queue import notify_machine_status
except ImportError:
    # Fallback if import fails
    def notify_machine_status(*args, **kwargs):
        print(f"AgingMachine Notification: {args}")
        pass


class AgingMachine(BaseMachine):

    def __init__(
        self,
        process_name: str,
        aging_parameters: AgingParameters,
        aging_model: AgingModel = None,
        connection_string=None,
    ):
        super().__init__(process_name, aging_model, aging_parameters)

    def receive_model_from_previous_process(
        self, previous_model: FormationCyclingModel
    ):
        self.battery_model = AgingModel(previous_model)

    # def calculate_total_steps(self):
    #     if self.battery_model is not None and self.machine_parameters is not None:
    #         self.total_steps = int(self.machine_parameters.aging_time_days * 24 * 3600)

    # def step_logic(self, t: int):
    #     pass

    def run(self):
        if self.pre_run_check():
            self.turn_on()
            # Notify start of aging process
            aging_time_hours = self.machine_parameters.aging_time_days * 24
            total_seconds = int(aging_time_hours * 3600)
            notify_machine_status(
                machine_id=self.process_name,
                line_type=self.process_name.split('_')[-1],
                process_name=self.process_name,
                status="aging_started",
                data={
                    "message": f"Starting {self.process_name} aging process",
                    "aging_time_days": self.machine_parameters.aging_time_days,
                    "aging_time_hours": aging_time_hours,
                    "total_seconds": total_seconds,
                    "temperature": self.machine_parameters.temperature
                }
            )
            # the range can be adjusted based on real process time
            time_range = list(range(0, total_seconds + 1, 3600))
            total_steps = len(time_range)
            current_step = 0
            for t in time_range:
                self.total_time = t
                current_step += 1
                self.battery_model.update_properties(self.machine_parameters, t)
                # Send progress updates every 24 steps (every day) or at key milestones
                if current_step % 24 == 0 or current_step == total_steps:
                    progress = (current_step / total_steps) * 100
                    hours_elapsed = t / 3600
                    days_elapsed = hours_elapsed / 24
                    notify_machine_status(
                        machine_id=self.process_name,
                        line_type=self.process_name.split('_')[-1],
                        process_name=self.process_name,
                        status="aging_progress",
                        data={
                            "message": f"Aging progress: {progress:.1f}% ({days_elapsed:.1f} days elapsed)",
                            "time_seconds": t,
                            "hours_elapsed": hours_elapsed,
                            "days_elapsed": days_elapsed,
                            "step": current_step,
                            "total_steps": total_steps,
                            "progress_percent": progress
                        }
                    )
            # Notify completion - this is the final stage!
            notify_machine_status(
                machine_id=self.process_name,
                line_type=self.process_name.split('_')[-1],
                process_name=self.process_name,
                status="aging_completed",
                data={
                    "message": f"🎉 COMPLETE: {self.process_name} aging completed! Battery manufacturing finished!",
                    "aging_time_completed": self.machine_parameters.aging_time_days,
                    "final_state": self.get_current_state(),
                    "manufacturing_complete": True
                }
            )
            
            self.turn_off()

    def validate_parameters(self, parameters: dict):
        return AgingParameters(**parameters).validate_parameters()
