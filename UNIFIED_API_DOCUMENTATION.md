# Unified `/api/simulation/start` Endpoint Documentation

## Overview
 The `/api/simulation/start` endpoint has been enhanced to support both full factory simulations and individual machine simulations with parameters for all machine types.

## Endpoint: `POST /api/simulation/start`

### Two Modes Available:

## 1. Full Factory Simulation (`mode: "full"`)
Runs the complete battery manufacturing process with all machines in sequence.

### Request Format:
```json
{
  "mode": "full",
  "anode_params": {
    "PVDF": 0.05,
    "CA": 0.045,
    "AM": 0.495,
    "Solvent": 0.41
  },
  "cathode_params": {
    "PVDF": 0.098,
    "CA": 0.039,
    "AM": 0.513,
    "Solvent": 0.35
  },
  "coating_params": {
    "coating_speed": 0.05,
    "gap_height": 0.0002,
    "flow_rate": 0.000005,
    "coating_width": 0.5
  },
  "drying_params": {
    "web_speed": 0.05
  },
  "calendaring_params": {
    "roll_gap": 0.0001,
    "roll_pressure": 5000000,
    "temperature": 80,
    "roll_speed": 0.1,
    "dry_thickness": 0.0001,
    "initial_porosity": 0.4
  },
  "slitting_params": {
    "blade_sharpness": 1.0,
    "slitting_speed": 0.1,
    "target_width": 0.5,
    "slitting_tension": 50.0
  },
  "inspection_params": {
    "epsilon_width_max": 0.1,
    "epsilon_thickness_max": 0.00001,
    "B_max": 2.0,
    "D_surface_max": 3.0
  },
  "rewinding_params": {
    "rewinding_speed": 0.5,
    "initial_tension": 100.0,
    "tapering_steps": 5.0,
    "environment_humidity": 45.0
  },
  "electrolyte_filling_params": {
    "Vacuum_level": 0.1,
    "Vacuum_filling": 0.8,
    "Soaking_time": 300
  },
  "formation_cycling_params": {
    "Charge_current_A": 2.0,
    "Charge_voltage_limit_V": 4.2,
    "Initial_Voltage": 3.0,
    "Formation_duration_s": 7200
  },
  "aging_params": {
    "k_leak": 0.001,
    "temperature": 60.0,
    "aging_time_days": 30.0
  }
}
```

### Response:
```json
{
  "message": "Full factory simulation started successfully",
  "mode": "full",
  "batch_id": "12345678-1234-1234-1234-123456789abc",
  "anode_params": { ... },
  "cathode_params": { ... },
  "updated_machine_params": ["coating_params", "drying_params", "calendaring_params", ...]
}
```

## 2. Individual Machine Simulation (`mode: "individual"`)
Runs a single machine simulation with specific parameters.

### Request Format:
```json
{
  "mode": "individual",
  "machine_type": "coating",
  "electrode_type": "Anode",
  "parameters": {
    "coating_speed": 0.05,
    "gap_height": 0.0002,
    "flow_rate": 0.000005,
    "coating_width": 0.5
  }
}
```

### Response:
```json
{
  "message": "Individual coating simulation started successfully",
  "mode": "individual",
  "machine_type": "coating",
  "electrode_type": "Anode",
  "parameters": { ... },
  "simulation_started": true
}
```

## Supported Machine Types for Individual Simulation:

| Machine Type | Requires electrode_type | Parameter Fields |
|--------------|------------------------|------------------|
| `mixing` | Yes (Anode/Cathode) | PVDF, CA, AM, Solvent |
| `coating` | Yes (Anode/Cathode) | coating_speed, gap_height, flow_rate, coating_width |
| `drying` | Yes (Anode/Cathode) | web_speed |
| `calendaring` | Yes (Anode/Cathode) | roll_gap, roll_pressure, temperature, roll_speed, dry_thickness, initial_porosity |
| `slitting` | Yes (Anode/Cathode) | blade_sharpness, slitting_speed, target_width, slitting_tension |
| `inspection` | Yes (Anode/Cathode) | epsilon_width_max, epsilon_thickness_max, B_max, D_surface_max |
| `rewinding` | No | rewinding_speed, initial_tension, tapering_steps, environment_humidity |
| `electrolyte_filling` | No | Vacuum_level, Vacuum_filling, Soaking_time |
| `formation_cycling` | No | Charge_current_A, Charge_voltage_limit_V, Initial_Voltage, Formation_duration_s |
| `aging` | No | k_leak, temperature, aging_time_days |

## Benefits of Unified Endpoint:

✅ **Single API endpoint** for all simulation needs
✅ **Backward compatible** with existing full simulation functionality  
✅ **Flexible parameter passing** - only provide parameters for machines you want to customize
✅ **Full validation** for all parameter types
✅ **WebSocket notifications** for real-time status updates
✅ **Individual machine testing** capability
✅ **Consistent error handling** across all machine types

## Frontend Integration Example:

```javascript
// Full simulation with all custom parameters
const fullSimulation = {
  mode: "full",
  anode_params: { PVDF: 0.05, CA: 0.045, AM: 0.495, Solvent: 0.41 },
  cathode_params: { PVDF: 0.098, CA: 0.039, AM: 0.513, Solvent: 0.35 },
  coating_params: { coating_speed: 0.05, gap_height: 0.0002, flow_rate: 0.000005, coating_width: 0.5 },
  drying_params: { web_speed: 0.05 },
  // ... other machine parameters
};

// Individual machine simulation
const individualSimulation = {
  mode: "individual",
  machine_type: "coating",
  electrode_type: "Anode", 
  parameters: { coating_speed: 0.05, gap_height: 0.0002, flow_rate: 0.000005, coating_width: 0.5 }
};

// Use the same endpoint for both
const response = await axios.post('/api/simulation/start', fullSimulation);
// or
const response = await axios.post('/api/simulation/start', individualSimulation);
```

## Summary:
**Yes, your team can use the single `/api/simulation/start` endpoint for everything!** It supports:
- Full factory simulations with custom parameters for all machines
- Individual machine simulations for testing specific components  
- Backward compatibility with existing mixing-only functionality
- All machine types with proper parameter validation
- Real-time WebSocket status updates