from fastapi import WebSocket
from typing import Optional
from simulation.event_bus.events import EventBus, PlantSimulationEventType


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.event_bus: Optional[EventBus] = None
        self.event_handlers = None

    def set_event_bus(self, event_bus: EventBus, event_handlers):
        """Set the event bus and handlers for this WebSocket manager."""
        self.event_bus = event_bus
        self.event_handlers = event_handlers
        self._subscribe_to_events()

    def _subscribe_to_events(self):
        """Subscribe to relevant machine events."""
        if not self.event_bus or not self.event_handlers:
            return
        
        # Subscribe to all machine events for WebSocket broadcasting
        for event_type in PlantSimulationEventType:
            self.event_bus.subscribe(
                event_type, 
                self.event_handlers.handle_machine_event_for_websocket
            )

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            # Remove disconnected websocket
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)

        # Remove disconnected connections
        for connection in disconnected:
            self.disconnect(connection)


websocket_manager = ConnectionManager()
