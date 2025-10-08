"""
Event system for decoupling simulation logic from notification logic.
Machines emit events, and other components can listen to these events.
"""

from dataclasses import dataclass
from datetime import datetime
from logging import error
from typing import Dict, Any, Callable, List
from enum import Enum


class PlantSimulationEventType(Enum):
    """Types of events that machines can emit."""

    # whenever a machine is turned on to process a batch
    MACHINE_TURNED_ON = "machine_turned_on"
    # whenever a machine is turned off to process a batch
    MACHINE_TURNED_OFF = "machine_turned_off"
    MACHINE_SIMULATION_ERROR = "machine_simulation_error"
    MACHINE_DATA_GENERATED = "data_generated"
    # for plant simulation
    BATCH_REQUESTED = "batch_requested"
    BATCH_STARTED_PROCESSING = "batch_started_processing"
    BATCH_STARTED_ANODE_LINE = "batch_started_anode_line"
    BATCH_STARTED_CATHODE_LINE = "batch_started_cathode_line"
    BATCH_COMPLETED_ANODE_LINE = "batch_completed_anode_line"
    BATCH_COMPLETED_CATHODE_LINE = "batch_completed_cathode_line"
    BATCH_ASSEMBLED = "batch_merged"
    BATCH_STARTED_CELL_LINE = "batch_started_cell_line"
    BATCH_COMPLETED_CELL_LINE = "batch_completed_cell_line"
    BATCH_COMPLETED = "batch_completed"


@dataclass
class PlantSimulationEvent:
    """Represents an event emitted by the plant simulation."""

    event_type: PlantSimulationEventType
    timestamp: str = None
    data: Dict[str, Any] = None


class EventBus:
    """
    Simple event bus for machine events.
    Machines emit events, listeners can subscribe to specific event types.
    """

    def __init__(self):
        """listeners example:
        {
            PlantSimulationEventType.BATCH_STARTED_ANODE_LINE: [callback_x],
            PlantSimulationEventType.BATCH_STARTED_CATHODE_LINE: [callback_y],
            PlantSimulationEventType.BATCH_MERGED: [callback_z],
            PlantSimulationEventType.BATCH_STARTED_CELL_LINE: [callback_a],
            PlantSimulationEventType.BATCH_COMPLETED: [callback_b],
            PlantSimulationEventType.BATCH_ERROR: [callback_c],
        }
        """
        self.__listeners: Dict[PlantSimulationEventType, List[Callable]] = {}

    def subscribe(
        self,
        event_type: PlantSimulationEventType,
        callback: Callable[[PlantSimulationEvent], None],
    ):
        """Subscribe to events of a specific type.
        For example, if the event type is MachineEventType.TURNED_ON, the callback (callback_x) will be called when the machine is turned on.
        The _listeners dict at this point after subscribing to the event type is:
        {
            MachineEventType.TURNED_ON: [callback_x],
        }
        """
        # check if the event type is already in the listeners.
        if event_type not in self.__listeners:
            self.__listeners[event_type] = []
        # add the callback to the listeners. This callback will be executed when the event is emitted.
        self.__listeners[event_type].append(callback)

    def unsubscribe(
        self,
        event_type: PlantSimulationEventType,
        callback: Callable[[PlantSimulationEvent], None],
    ):
        """Unsubscribe from events."""
        if event_type in self.__listeners:
            try:
                self.__listeners[event_type].remove(callback)
            except ValueError:
                pass

    def __emit(self, event: PlantSimulationEvent):
        """Emit an event to all subscribers."""
        # check the event type is in the listeners
        if event.event_type in self.__listeners:
            # call all of the callbacks for the event type.
            for callback in self.__listeners[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    # general error handling for the event callback
                    error(f"Error in event callback: {e}")

    def emit_plant_simulation_event(
        self,
        event_type: PlantSimulationEventType,
        data: Dict[str, Any] = None,
    ):
        """Emit a plant simulation event."""
        event = PlantSimulationEvent(
            event_type=event_type,
            timestamp=datetime.now().isoformat(),
            data=data or {},
        )
        self.__emit(event)
