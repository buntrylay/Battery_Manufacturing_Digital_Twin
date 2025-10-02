from simulation.machine.BaseMachine import BaseMachine
from dataclasses import dataclass
from simulation.process_parameters.Parameters import RewindingParameters
from simulation.battery_model.RewindingModel import RewindingModel
from simulation.battery_model import ElectrodeInspectionModel

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
        print(f"RewindingMachine Notification: {args}")
        pass


class RewindingMachine(BaseMachine):
    def __init__(
        self,
        process_name: str,
        rewinding_parameters: RewindingParameters,
        rewinding_model: RewindingModel = None,
        connection_string=None,
    ):
        super().__init__(
            process_name,
            rewinding_model,
            rewinding_parameters,
        )

    def receive_model_from_previous_process(
        self,
        assembled_rewinding_model: RewindingModel,
    ):
        self.battery_model = assembled_rewinding_model

    def run(self, end_time=120, step=5):
        self.turn_on()
        
        # Notify start of rewinding process
        notify_machine_status(
            machine_id=self.process_name,
            line_type=self.process_name.split('_')[-1],
            process_name=self.process_name,
            status="rewinding_started",
            data={
                "message": f"Starting {self.process_name} rewinding process",
                "end_time": end_time,
                "step_size": step,
                "total_steps": len(range(0, end_time + 1, step))
            }
        )
        
        all_results = []
        total_steps = len(range(0, end_time + 1, step))
        current_step = 0

        for t in range(0, end_time + 1, step):
            self.total_time = t
            current_step += 1
            
            self.battery_model.update_properties(self.machine_parameters)
            result = self.get_current_state()
            all_results.append(result)
            self.save_data_to_local_folder()
            
            # Send progress updates every 5 steps or at key milestones
            if current_step % 5 == 0 or current_step == total_steps:
                progress = (current_step / total_steps) * 100
                notify_machine_status(
                    machine_id=self.process_name,
                    line_type=self.process_name.split('_')[-1],
                    process_name=self.process_name,
                    status="rewinding_progress",
                    data={
                        "message": f"Rewinding progress: {progress:.1f}%",
                        "time": t,
                        "end_time": end_time,
                        "step": current_step,
                        "total_steps": total_steps,
                        "progress_percent": progress
                    }
                )
        
        self.save_all_results(all_results)
        
        # Notify completion
        notify_machine_status(
            machine_id=self.process_name,
            line_type=self.process_name.split('_')[-1],
            process_name=self.process_name,
            status="rewinding_completed",
            data={
                "message": f"{self.process_name} rewinding completed successfully",
                "total_results": len(all_results),
                "final_state": self.get_current_state()
            }
        )
        
        self.turn_off()

    def validate_parameters(self, parameters: dict):
        return RewindingParameters(**parameters).validate_parameters()
