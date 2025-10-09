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
