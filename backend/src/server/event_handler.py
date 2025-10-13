"""Centralised event handling for WebSocket broadcasting and database storage."""

import asyncio
import json
from logging import error, info, warning
from typing import Any, Callable, Dict, Optional, TYPE_CHECKING

from simulation.event_bus.events import PlantSimulationEvent, PlantSimulationEventType

if TYPE_CHECKING:
    from simulation.factory.PlantSimulation import PlantSimulation
    from websocket_manager import ConnectionManager
    from db.db_helper import DBHelper


class EventHandler:
    """Routes simulation events to external systems from a single place."""

    def __init__(
        self,
        plant_simulation: "PlantSimulation",
        websocket_manager: "ConnectionManager",
        database_helper: Optional["DBHelper"] = None,
    ):
        self.__plant_simulation = plant_simulation
        self.__websocket_manager = websocket_manager
        self.__database_helper = database_helper
        self.__subscriptions_initialised = False

    def initialise_system_subscriptions(self):
        """Subscribe to all relevant simulation events once."""
        if self.__subscriptions_initialised:
            return

        websocket_subscriptions: list[
            tuple[
                PlantSimulationEventType,
                Callable[[PlantSimulationEvent], None],
                bool,
            ]
        ] = [
            (
                event_type,
                self.__broadcast_system_notification,
                True,  # Enable batch context for all events
            )
            for event_type in PlantSimulationEventType
            if event_type != PlantSimulationEventType.MACHINE_DATA_GENERATED
        ]

        database_subscriptions: list[
            tuple[
                PlantSimulationEventType,
                Callable[[PlantSimulationEvent], None],
                bool,
            ]
        ] = []

        if self.__database_helper is not None:
            database_subscriptions = [
                (
                    PlantSimulationEventType.BATCH_REQUESTED,
                    self.__queue_machine_data,
                    False,
                ),
                (
                    PlantSimulationEventType.MACHINE_DATA_GENERATED,
                    self.__queue_machine_data,
                    True,
                ),
            ]

        all_subscriptions = websocket_subscriptions + database_subscriptions

        for event_type, callback, include_batch in all_subscriptions:
            self.__plant_simulation.subscribe_to_event(
                event_type,
                callback,
                include_batch_context=include_batch,
            )

        self.__subscriptions_initialised = True

    # ------------------------------------------------------------------
    # Database helpers
    # ------------------------------------------------------------------
    def __queue_machine_data(self, event: PlantSimulationEvent):
        if self.__database_helper is None or event.event_type not in [
            PlantSimulationEventType.MACHINE_DATA_GENERATED,
            PlantSimulationEventType.BATCH_REQUESTED,
        ]:
            return

        payload: Dict[str, Any] = {
            "event_type": event.event_type.value,
            "timestamp": event.timestamp,
            **event.data,
        }

        try:
            machine_state = payload.get("machine_state")
            if machine_state:
                self.__database_helper.queue_data(machine_state)
            pass
            # info(
            #     f"[{payload.get("timestamp")}] POSTGRESQL: Queued payload into database queue with event type: {payload.get('event_type')} for batch - id: {payload.get("batch_id")}"
            # )
        except Exception as exc:
            error(
                f"POSTGRESQL - ERROR: Error enqueuing payload into database queue with event type: {payload.get('event_type')}"
            )

    # ------------------------------------------------------------------
    # WebSocket helpers
    # ------------------------------------------------------------------
    def __broadcast_system_notification(self, event: PlantSimulationEvent):
        """This method acts as the adapter to the prev. version of the websocket broadcast"""
        # legacy structure from the prev. version
        event_data = event.data or {}

        if "machine_id" in event_data:
            process_name = event_data.get("machine_id")
        else:
            process_name = "battery_plant_simulation"

        processed_notification = {
            "process_name": process_name,
            "status": event.event_type.value,
            "timestamp": event.timestamp,
            "data": event_data,
        }

        self.__schedule_websocket_broadcast(processed_notification)

    def __schedule_websocket_broadcast(self, notification: Dict[str, Any]):
        try:
            # get event loop
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = None
        # if there is a current process in the loop create a task first
        if loop and loop.is_running():
            # __broadcast_to_websocket is async function
            asyncio.create_task(self.__broadcast_to_websocket(notification))
        else:
            # otherwise, execute it
            asyncio.run(self.__broadcast_to_websocket(notification))

    async def __broadcast_to_websocket(self, notification: Dict[str, Any]):
        try:
            message = json.dumps(notification)
            await self.__websocket_manager.broadcast(message)
            # for testing only
            info(
                f'WEBSOCKET: Batch ({notification.get("data").get("batch_id")}) Successfully broadcasting an event - {notification.get("status")} from {notification.get("process_name")}',
            )
        except Exception as exc:
            error(
                f'WEBSOCKET: Error broadcasting an event status {notification.get("status")}: {exc}'
            )
