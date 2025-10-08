export const stageDescriptions = {
  "Anode Mixing": "Mixes anode active material, binder, and solvent.",
  "Cathode Mixing": "Mixes cathode active material, binder, and solvent.",
  "Anode Coating": "Applies slurry onto current collectors.",
  "Cathode Coating": "Applies slurry onto current collectors.",
  "Anode Drying": "Removes solvent and solidifies coating.",
  "Cathode Drying": "Removes solvent and solidifies coating.",
  "Anode Calendaring": "Compresses electrode sheets.",
  "Cathode Calendaring": "Compresses electrode sheets.",
  "Anode Slitting": "Cuts electrode rolls.",
  "Cathode Slitting": "Cuts electrode rolls.",
  "Anode Inspection": "Checks electrode quality.",
  "Cathode Inspection": "Checks electrode quality.",
  Rewinding: "Re-rolls electrodes under controlled tension.",
  "Electrolyte Filling": "Injects electrolyte into cells.",
  "Formation Cycling": "Runs charge/discharge cycles to form SEI.",
  Aging: "Stabilizes cells to ensure reliability.",
};

export const inputsByStage = {
  "Anode Mixing": ["Anode PVDF", "Anode CA", "Anode AM", "Anode Solvent"],
  "Cathode Mixing": [
    "Cathode PVDF",
    "Cathode CA",
    "Cathode AM",
    "Cathode Solvent",
  ],

  "Anode Coating": [
    "Coating Speed",
    "Gap Height",
    "Flow Rate",
    "Coating Width",
  ],
  "Cathode Coating": [
    "Coating Speed",
    "Gap Height",
    "Flow Rate",
    "Coating Width",
  ],

  "Anode Drying": ["Web Speed"],
  "Cathode Drying": ["Web Speed"],

  "Anode Calendaring": ["Roll Gap", "Roll Pressure", "Temperature", "Roll Speed", "Dry Thickness", "Initial Porosity"],
  "Cathode Calendaring": ["Roll Gap", "Roll Pressure", "Temperature", "Roll Speed", "Dry Thickness", "Initial Porosity"],

  "Anode Slitting": ["Blade Sharpness", "Slitting Speed", "Target Width", "Slitting Tension"],
  "Cathode Slitting": ["Blade Sharpness", "Slitting Speed", "Target Width", "Slitting Tension"],

  "Anode Inspection": [
    "Epsilon Width Max",
    "Epsilon Thickness Max",
    "B Max",
    "D Surface Max",
  ],
  "Cathode Inspection": [
    "Epsilon Width Max",
    "Epsilon Thickness Max",
    "B Max",
    "D Surface Max",
  ],

  Rewinding: ["Rewinding Speed", "Initial Tension", "Tapering Steps", "Environment Humidity"],
  "Electrolyte Filling": ["Vacuum Level", "Vacuum Filling", "Soaking Time"],
  "Formation Cycling": ["Charge Current A", "Charge Voltage Limit V", "Initial Voltage", "Formation Duration s"],
  Aging: ["K Leak", "Temperature", "Aging Time Days"],
};

// Mapping from frontend field names to backend parameter names
export const fieldToParameterMapping = {
  // Mixing (already handled separately)
  
  // Coating
  "Coating Speed": "coating_speed",
  "Gap Height": "gap_height",
  "Flow Rate": "flow_rate",
  "Coating Width": "coating_width",
  
  // Drying
  "Web Speed": "web_speed",
  
  // Calendaring
  "Roll Gap": "roll_gap",
  "Roll Pressure": "roll_pressure",
  "Calendaring Temperature": "temperature",
  "Roll Speed": "roll_speed",
  "Dry Thickness": "dry_thickness",
  "Initial Porosity": "initial_porosity",
  
  // Slitting
  "Blade Sharpness": "blade_sharpness",
  "Slitting Speed": "slitting_speed",
  "Target Width": "target_width",
  "Slitting Tension": "slitting_tension",
  
  // Electrode Inspection
  "Epsilon Width Max": "epsilon_width_max",
  "Epsilon Thickness Max": "epsilon_thickness_max",
  "B Max": "B_max",
  "D Surface Max": "D_surface_max",
  
  // Rewinding
  "Rewinding Speed": "rewinding_speed",
  "Initial Tension": "initial_tension",
  "Tapering Steps": "tapering_steps",
  "Environment Humidity": "environment_humidity",
  
  // Electrolyte Filling
  "Vacuum Level": "Vacuum_level",
  "Vacuum Filling": "Vacuum_filling",
  "Soaking Time": "Soaking_time",
  
  // Formation Cycling
  "Charge Current A": "Charge_current_A",
  "Charge Voltage Limit V": "Charge_voltage_limit_V",
  "Initial Voltage": "Initial_Voltage",
  "Formation Duration s": "Formation_duration_s",
  
  // Aging
  "K Leak": "k_leak",
  "Aging Temperature": "temperature",
  "Aging Time Days": "aging_time_days",
};

// Function to convert frontend inputs to backend parameter format
export const convertInputsToParameters = (stageId, inputValues) => {
  const parameters = {};
  
  // Handle mixing separately (already has its own logic)
  if (stageId.includes("Mixing")) {
    const electrodeType = stageId.includes("Anode") ? "Anode" : "Cathode";
    return {
      AM: parseFloat(inputValues[`${electrodeType} AM`] || 0),
      CA: parseFloat(inputValues[`${electrodeType} CA`] || 0),
      PVDF: parseFloat(inputValues[`${electrodeType} PVDF`] || 0),
      Solvent: parseFloat(inputValues[`${electrodeType} Solvent`] || 0),
    };
  }
  
  // For all other stages, convert using the mapping
  const fields = inputsByStage[stageId] || [];
  fields.forEach(field => {
    const backendParam = fieldToParameterMapping[field];
    if (backendParam && inputValues[field] !== undefined && inputValues[field] !== "") {
      // Convert to appropriate type (most are floats, Formation_duration_s is int)
      if (backendParam === "Formation_duration_s") {
        parameters[backendParam] = parseInt(inputValues[field], 10);
      } else {
        parameters[backendParam] = parseFloat(inputValues[field]);
      }
    }
  });
  
  return parameters;
};

// Mapping from stage ID to parameter class type and API endpoint
export const stageToParameterType = {
  "Anode Mixing": { type: "mixing", paramClass: "MixingParameters" },
  "Cathode Mixing": { type: "mixing", paramClass: "MixingParameters" },
  
  "Anode Coating": { type: "coating", paramClass: "CoatingParameters" },
  "Cathode Coating": { type: "coating", paramClass: "CoatingParameters" },
  
  "Anode Drying": { type: "drying", paramClass: "DryingParameters" },
  "Cathode Drying": { type: "drying", paramClass: "DryingParameters" },
  
  "Anode Calendaring": { type: "calendaring", paramClass: "CalendaringParameters" },
  "Cathode Calendaring": { type: "calendaring", paramClass: "CalendaringParameters" },
  
  "Anode Slitting": { type: "slitting", paramClass: "SlittingParameters" },
  "Cathode Slitting": { type: "slitting", paramClass: "SlittingParameters" },
  
  "Anode Inspection": { type: "inspection", paramClass: "ElectrodeInspectionParameters" },
  "Cathode Inspection": { type: "inspection", paramClass: "ElectrodeInspectionParameters" },
  
  "Rewinding": { type: "rewinding", paramClass: "RewindingParameters" },
  "Electrolyte Filling": { type: "electrolyte_filling", paramClass: "ElectrolyteFillingParameters" },
  "Formation Cycling": { type: "formation_cycling", paramClass: "FormationCyclingParameters" },
  "Aging": { type: "aging", paramClass: "AgingParameters" },
};
