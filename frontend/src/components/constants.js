export const stageIcons = {
  Mixing: "🧪",
  Coating: "🎨",
  Drying: "🌬️",
  Calendaring: "⚙️",
  Slitting: "✂️",
  Inspection: "🔍",
  Rewinding: "♻️",
  "Electrolyte Filling": "💧",
  "Formation Cycling": "🔋",
  Aging: "⏳",
};

export const stageDescriptions = {
  Mixing:
    "Combines active material, binder, and solvent into a uniform slurry.",
  Coating: "Applies the slurry onto current collectors at controlled speed.",
  Drying: "Removes solvent to solidify coating, ensuring consistent thickness.",
  Calendaring:
    "Compresses electrode sheets for density and mechanical strength.",
  Slitting: "Cuts wide electrode rolls into narrower strips.",
  Inspection: "Checks electrode quality, dimensions, and detects defects.",
  Rewinding: "Re-rolls electrodes under controlled tension.",
  "Electrolyte Filling":
    "Injects electrolyte into assembled cells under vacuum.",
  "Formation Cycling": "Performs charge/discharge cycles to form SEI layer.",
  Aging: "Stabilizes cells over time to ensure reliability.",
};

export const inputsByStage = {
  Mixing: ["PVDF", "CA", "AM", "Solvent"],
  Coating: ["Coating Speed", "Gap Height", "Flow Rate", "Coating Width"],
  Drying: ["Web Speed", "Drying Temp", "Drying Time"],
  Calendaring: ["Roll Gap", "Roll Pressure", "Roll Speed"],
  Slitting: ["Blade Sharpness", "Slitting Speed", "Target Width"],
  Inspection: ["Width Tolerance", "Thickness Tolerance", "Defects Allowed"],
  Rewinding: ["Rewinding Speed", "Initial Tension"],
  "Electrolyte Filling": ["Vacuum Level", "Vacuum Filling", "Soaking Time"],
  "Formation Cycling": ["Charge Current", "Voltage"],
  Aging: ["Leak Rate", "Temperature", "Aging Days"],
};
