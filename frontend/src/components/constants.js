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
    "Width Tolerance",
    "Thickness Tolerance",
    "B Max",
    "Defects Allowed",
  ],
  "Cathode Inspection": [
    "Width Tolerance",
    "Thickness Tolerance", 
    "B Max",
    "Defects Allowed",
  ],

  Rewinding: ["Rewinding Speed", "Initial Tension", "Tapering Steps", "Environment Humidity"],
  "Electrolyte Filling": ["Vacuum Level", "Vacuum Filling", "Soaking Time"],
  "Formation Cycling": ["Charge Current", "Voltage", "Initial Voltage"],
  Aging: ["Leak Rate", "Temperature", "Aging Days"],
};

// Units mapping for each parameter
export const parameterUnits = {
  // Mixing parameters (ratios - dimensionless, sum to 1.0)
  "Anode PVDF": "fraction",
  "Anode CA": "fraction", 
  "Anode AM": "fraction",
  "Anode Solvent": "fraction",
  "Cathode PVDF": "fraction",
  "Cathode CA": "fraction",
  "Cathode AM": "fraction", 
  "Cathode Solvent": "fraction",

  // Coating parameters
  "Coating Speed": "m/min",
  "Gap Height": "μm",
  "Flow Rate": "mL/min",
  "Coating Width": "mm",

  // Drying parameters
  "Web Speed": "m/min",

  // Calendaring parameters  
  "Roll Gap": "μm",
  "Roll Pressure": "MPa",
  "Temperature": "°C",
  "Roll Speed": "m/min", 
  "Dry Thickness": "μm",
  "Initial Porosity": "%",

  // Slitting parameters
  "Blade Sharpness": "units",
  "Slitting Speed": "m/min",
  "Target Width": "mm", 
  "Slitting Tension": "N/m",

  // Inspection parameters
  "Width Tolerance": "mm",
  "Thickness Tolerance": "μm",
  "B Max": "T", // Tesla for magnetic field
  "Defects Allowed": "count",

  // Rewinding parameters
  "Rewinding Speed": "m/min",
  "Initial Tension": "N/m",
  "Tapering Steps": "count",
  "Environment Humidity": "%",

  // Electrolyte Filling parameters
  "Vacuum Level": "Pa",
  "Vacuum Filling": "units",
  "Soaking Time": "min",

  // Formation Cycling parameters
  "Charge Current": "A",
  "Voltage": "V", 
  "Initial Voltage": "V",

  // Aging parameters
  "Leak Rate": "1/s",
  "Aging Days": "days"
};
