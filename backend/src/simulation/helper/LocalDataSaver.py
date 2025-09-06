import json
import os


class LocalDataSaver:
    """
    Handles persistence of simulation data to the local filesystem.
    """

    def __init__(self, process_name: str, base_output_dir: str | None = None):
        self.process_name = process_name
        base_dir = base_output_dir or os.getcwd()
        self.output_dir = os.path.join(base_dir, f"{process_name.lower()}_output")

    def ensure_output_dir(self) -> str:
        """
        Create the output directory if it doesn't exist and return its path.
        """
        os.makedirs(self.output_dir, exist_ok=True)
        return self.output_dir

    def save_current_state(self, state: dict, total_time_seconds: float) -> str:
        """
        Save a single timestep state to a timestamped JSON file.

        Args:
            state: JSON-serializable dictionary returned from get_current_state.
            total_time_seconds: Elapsed time for naming convenience only.

        Returns:
            The path of the file written.
        """
        self.ensure_output_dir()
        timestamp = state.get("timestamp", "").replace(":", "-").replace(".", "-")
        filename = f"{self.process_name.lower()}_{timestamp}_result_at_{round(total_time_seconds)}s.json"
        path = os.path.join(self.output_dir, filename)
        with open(path, "w") as f:
            json.dump(state, f)
        return path

    def save_all_results(self, results: dict) -> str:
        """
        Save the summary of all results to a single JSON file.
        """
        self.ensure_output_dir()
        path = os.path.join(self.output_dir, f"{self.process_name.lower()}_summary.json")
        with open(path, "w") as f:
            json.dump(results, f)
        return path


