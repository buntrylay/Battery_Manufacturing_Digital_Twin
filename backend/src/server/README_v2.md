# Battery Manufacturing Digital Twin V2 Server

This is the enhanced version of the server that properly leverages the `PlantSimulation` class and provides comprehensive parameter validation using the parameter classes.

## Key Features

### 1. **PlantSimulation Integration**
- Uses the `PlantSimulation` class as the core simulation engine
- Properly manages factory structure with anode, cathode, and cell production lines
- Supports batch processing with queue management
- Thread-safe operation with proper locking mechanisms

### 2. **Comprehensive Parameter Validation**
- Uses Pydantic models for input validation
- Validates all parameter types: Mixing, Coating, Drying, Calendaring, Slitting, etc.
- Ensures material ratios sum to 1.0 for mixing parameters
- Validates positive values and ranges for all parameters

### 3. **Real-time Communication**
- WebSocket support for real-time status updates
- Message queue system for broadcasting simulation progress
- Thread-safe message broadcasting

### 4. **Enhanced API Endpoints**

#### Core Simulation Endpoints
- `POST /start-simulation` - Start simulation with anode/cathode mixing parameters
- `POST /factory/start` - Add batch to factory queue with custom parameters
- `GET /factory/status` - Get comprehensive factory status
- `GET /factory/logs` - Get recent simulation logs

#### Machine Management Endpoints
- `GET /machine/{line_type}/{machine_id}/status` - Get machine status
- `PATCH /machine/{line_type}/{machine_id}/parameters` - Update machine parameters

#### WebSocket Endpoints
- `WS /ws/status` - Real-time status updates

#### Health Check
- `GET /health` - Health check with database connectivity

## API Usage Examples

### 1. Start Simple Simulation
```bash
curl -X POST "http://localhost:8000/start-simulation" \
  -H "Content-Type: application/json" \
  -d '{
    "anode": {
      "AM": 0.8,
      "CA": 0.1,
      "PVDF": 0.05,
      "solvent": 0.05
    },
    "cathode": {
      "AM": 0.9,
      "CA": 0.05,
      "PVDF": 0.03,
      "solvent": 0.02
    }
  }'
```

### 2. Add Custom Batch with Parameters
```bash
curl -X POST "http://localhost:8000/factory/start" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "batch_001",
    "anode_mixing_params": {
      "material_ratios": {
        "AM": 0.8,
        "CA": 0.1,
        "PVDF": 0.05,
        "solvent": 0.05
      }
    },
    "anode_coating_params": {
      "coating_speed": 0.1,
      "gap_height": 0.0002,
      "flow_rate": 0.000005,
      "coating_width": 0.5
    }
  }'
```

### 3. Update Machine Parameters
```bash
curl -X PATCH "http://localhost:8000/machine/anode/mixing/parameters" \
  -H "Content-Type: application/json" \
  -d '{
    "material_ratios": {
      "AM": 0.85,
      "CA": 0.08,
      "PVDF": 0.04,
      "solvent": 0.03
    }
  }'
```

### 4. Get Machine Status
```bash
curl "http://localhost:8000/machine/anode/mixing/status"
```

### 5. Get Factory Status
```bash
curl "http://localhost:8000/factory/status"
```

## WebSocket Usage

Connect to the WebSocket endpoint for real-time updates:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/status');

ws.onmessage = function(event) {
    console.log('Received:', event.data);
};

ws.onopen = function() {
    console.log('Connected to simulation updates');
};
```

## Parameter Classes

The server supports the following parameter types with full validation:

### MixingParameters
- Material ratios (AM, CA, PVDF, solvent) that must sum to 1.0
- All ratios must be positive

### CoatingParameters
- coating_speed: Coating speed in m/s
- gap_height: Gap height in meters
- flow_rate: Flow rate in m³/s
- coating_width: Coating width in meters

### DryingParameters
- wet_thickness: Wet thickness in meters
- solid_content: Solid content ratio (0-1)
- web_speed: Web speed in m/s

### CalendaringParameters
- roll_gap: Roll gap in meters
- roll_pressure: Roll pressure in Pa
- temperature: Temperature in K
- roll_speed: Roll speed in m/s
- dry_thickness: Dry thickness in meters
- initial_porosity: Initial porosity (0-1)

### And more...
- SlittingParameters
- ElectrodeInspectionParameters
- RewindingParameters
- ElectrolyteFillingParameters
- FormationCyclingParameters
- AgingParameters

## Error Handling

The server provides comprehensive error handling:

- **400 Bad Request**: Invalid parameters or validation failures
- **404 Not Found**: Machine or line type not found
- **500 Internal Server Error**: Server-side errors

All errors include descriptive messages to help with debugging.

## Thread Safety

The server uses proper locking mechanisms:
- `simulation_lock`: Prevents concurrent simulations
- `message_lock`: Thread-safe message queue operations
- Thread-safe WebSocket broadcasting

## Database Integration

The server includes optional PostgreSQL integration for data persistence and health checks.

## Running the Server

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python v2_server.py

# Or with uvicorn
uvicorn v2_server:app --host 0.0.0.0 --port 8000 --reload
```

## Differences from main.py

1. **Proper PlantSimulation Usage**: Uses the factory structure and batch processing
2. **Comprehensive Validation**: All inputs are validated using parameter classes
3. **Enhanced API**: More endpoints for machine and factory management
4. **Better Error Handling**: Detailed error messages and proper HTTP status codes
5. **Thread Safety**: Proper locking and thread management
6. **Extensibility**: Easy to add new machine types and parameters
