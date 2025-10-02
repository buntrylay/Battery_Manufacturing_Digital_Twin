# Decoupled Notification Architecture

## Problem Solved

Previously, machines were tightly coupled to the notification system, making them responsible for both simulation logic AND WebSocket communication. This violated separation of concerns and made machines harder to test and maintain.

## New Architecture

### Event-Driven Design

```txt
Machines → Events → PlantSimulation → Notifications → WebSocket Server
```

### Components

#### 1. Event System (`simulation/events.py`)

- **EventBus**: Simple pub/sub system for machine events
- **MachineEvent**: Structured event data
- **MachineEventType**: Enum of event types (TURNED_ON, TURNED_OFF, etc.)

#### 2. Machines (Updated)

- **Before**: Direct calls to `notify_machine_status()`
- **After**: Emit events via `event_bus.emit_machine_event()`
- **Benefit**: Focus purely on simulation logic

#### 3. PlantSimulation (Updated)

- **New Role**: Event listener and notification converter
- **Responsibility**: Convert machine events to WebSocket notifications
- **Benefit**: Centralized notification handling

#### 4. NotificationQueue (Unchanged)

- Still handles async/sync bridge
- Still manages WebSocket communication
- No changes to existing functionality

## Benefits

### 1. **Separation of Concerns**
- Machines: Pure simulation logic
- PlantSimulation: Event handling and coordination
- NotificationQueue: WebSocket communication

### 2. **Testability**
- Machines can be tested without WebSocket dependencies
- Event system can be tested independently
- PlantSimulation can be tested with mock events

### 3. **Maintainability**
- Changes to notification logic don't affect machines
- New event types can be added easily
- Clear responsibility boundaries

### 4. **Extensibility**
- Other components can listen to machine events
- Multiple notification handlers possible
- Event filtering/routing can be added

## Usage Example

```python
# Machine emits event (simple, lightweight)
event_bus.emit_machine_event(
    machine_id="mixing_anode",
    line_type="anode",
    process_name="mixing_anode", 
    event_type=MachineEventType.TURNED_ON,
    data={"temperature": 25.0}
)

# PlantSimulation automatically converts to notification
# NotificationQueue handles WebSocket distribution
```

## Migration Impact

- **Machines**: Minimal changes, just event emission instead of direct notifications
- **PlantSimulation**: Added event listener setup
- **WebSocket Server**: No changes needed
- **Frontend**: No changes needed

## Future Enhancements

1. **Event Filtering**: Only send certain events to WebSocket
2. **Event Persistence**: Store events for debugging/analytics
3. **Multiple Handlers**: Different handlers for different event types
4. **Event Metrics**: Track event frequency and performance
