"""
Event handlers for converting machine events to WebSocket and database notifications.
This module provides clean separation between event bus and external systems.
"""

import json
import asyncio
from typing import Dict, Any
from simulation.event_bus.events import MachineEvent, PlantSimulationEventType
from .WebSocketManager import websocket_manager
from .db.db_helper import database_helper


class EventHandler:
    """Handles conversion of machine events to external system notifications."""

    def __init__(self):
        pass

    def handle_machine_event_for_websocket(self, event: MachineEvent):
        """Convert machine event to WebSocket notification."""
        # Map event types to notification statuses
        status_mapping = {
            PlantSimulationEventType.MACHINE_TURNED_ON: "running",
            PlantSimulationEventType.MACHINE_TURNED_OFF: "idle",
            PlantSimulationEventType.MACHINE_SIMULATION_ERROR: "error",
            PlantSimulationEventType.MACHINE_DATA_GENERATED: "data_generated",
            PlantSimulationEventType.BATCH_REQUESTED: "batch_requested",
            PlantSimulationEventType.BATCH_STARTED_ANODE_LINE: "batch_started_anode_line",
            PlantSimulationEventType.BATCH_STARTED_CATHODE_LINE: "batch_started_cathode_line",
            PlantSimulationEventType.BATCH_ASSEMBLED: "batch_merged",
            PlantSimulationEventType.BATCH_STARTED_CELL_LINE: "batch_started_cell_line",
            PlantSimulationEventType.BATCH_COMPLETED: "batch_completed",
            PlantSimulationEventType.BATCH_ERROR: "batch_error",
        }

        status = status_mapping.get(event.event_type, "unknown")

        # Create notification payload
        notification = {
            "process_name": event.machine_id,
            "status": status,
            "timestamp": event.timestamp,
            "data": event.data or {},
        }

        # Broadcast to WebSocket clients
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self._broadcast_to_websocket(notification))
            else:
                loop.run_until_complete(self._broadcast_to_websocket(notification))
        except RuntimeError:
            # If no event loop is running, create a new one
            asyncio.run(self._broadcast_to_websocket(notification))

    async def _broadcast_to_websocket(self, notification: Dict[str, Any]):
        """Broadcast notification to all WebSocket clients."""
        try:
            message = json.dumps(notification)
            await websocket_manager.broadcast(message)
        except Exception as e:
            print(f"Error broadcasting to WebSocket: {e}")

    def handle_machine_event_for_database(self, event: MachineEvent):
        """Convert machine event to database record."""
        # Only save data events to database
        if event.event_type == PlantSimulationEventType.MACHINE_DATA_GENERATED:
            try:
                # Add event metadata to the data
                db_payload = {
                    "machine_id": event.machine_id,
                    "event_type": event.event_type.value,
                    "timestamp": event.timestamp,
                    **event.data,
                }
                database_helper.queue_data(db_payload)
            except Exception as e:
                print(f"Error queuing data for database: {e}")

    def handle_plant_simulation_event_for_websocket(self, event):
        """Handle plant simulation events for WebSocket."""
        # Create notification for plant-level events
        notification = {
            "process_name": "plant_simulation",
            "status": event.event_type.value,
            "timestamp": event.timestamp,
            "data": event.data or {},
        }

        # Broadcast to WebSocket clients
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(self._broadcast_to_websocket(notification))
            else:
                loop.run_until_complete(self._broadcast_to_websocket(notification))
        except RuntimeError:
            asyncio.run(self._broadcast_to_websocket(notification))
