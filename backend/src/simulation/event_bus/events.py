"""
Event system for decoupling simulation logic from notification logic.
Machines emit events, and other components can listen to these events.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Callable, List
from enum import Enum


class MachineEventType(Enum):
    """Types of events that machines can emit. 
    Types of notifications that can be sent to any software component.
    """
    TURNED_ON = "turned_on"
    TURNED_OFF = "turned_off"
    PROCESS_STARTED = "process_started"
    PROCESS_COMPLETED = "process_completed"
    PROCESS_ERROR = "process_error"
    STATUS_UPDATE = "status_update"
    DATA_UPDATE = "data_update"


@dataclass
class MachineEvent:
    """Represents an event emitted by a machine."""
    machine_id: str
    event_type: MachineEventType
    timestamp: str
    data: Dict[str, Any] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class EventBus:
    """
    Simple event bus for machine events.
    Machines emit events, listeners can subscribe to specific event types.
    """

    def __init__(self):
        self._listeners: Dict[MachineEventType, List[Callable]] = {}

    def subscribe(
        self, event_type: MachineEventType, callback: Callable[[MachineEvent], None]
    ):
        """Subscribe to events of a specific type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def unsubscribe(
        self, event_type: MachineEventType, callback: Callable[[MachineEvent], None]
    ):
        """Unsubscribe from events."""
        if event_type in self._listeners:
            try:
                self._listeners[event_type].remove(callback)
            except ValueError:
                pass

    def emit(self, event: MachineEvent):
        """Emit an event to all subscribers."""
        if event.event_type in self._listeners:
            for callback in self._listeners[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    print(f"Error in event callback: {e}")

    def emit_machine_event(
        self,
        machine_id: str,
        event_type: MachineEventType,
        data: Dict[str, Any] = None,
    ):
        """Convenience method to emit a machine event."""
        event = MachineEvent(
            machine_id=machine_id,
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            data=data or {},
        )
        self.emit(event)
