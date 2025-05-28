from abc import ABC, abstractmethod
from typing import Dict, Any

class ProcessCalculator(ABC):
    @abstractmethod
    def calculate_properties(self, state_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate properties based on the current state data."""
        pass 