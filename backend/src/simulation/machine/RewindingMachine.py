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
        # self.total_steps = 120 // 5

    def receive_model_from_previous_process(
        self,
        assembled_rewinding_model: RewindingModel,
    ):
        self.battery_model = assembled_rewinding_model

    def step_logic(self, t: int):
        pass

    def validate_parameters(self, parameters: dict):
        return RewindingParameters(**parameters).validate_parameters()
