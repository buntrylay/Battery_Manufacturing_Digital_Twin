// Parameter validation rules and ranges for all machine types
// These ranges are derived from typical battery manufacturing parameters

export const parameterValidation = {
  // Mixing parameters (must sum to 1.0)
  mixing: {
    "AM": { min: 0.1, max: 0.9, step: 0.001, description: "Active Material ratio" },
    "CA": { min: 0.01, max: 0.3, step: 0.001, description: "Conductive Additive ratio" },
    "PVDF": { min: 0.01, max: 0.2, step: 0.001, description: "Binder ratio" },
    "Solvent": { min: 0.01, max: 0.5, step: 0.001, description: "Solvent ratio" }
  },

  // Coating parameters
  coating: {
    "Coating Speed": { min: 1, max: 100, step: 0.1, unit: "m/min", description: "Web coating speed" },
    "Gap Height": { min: 0.05, max: 0.5, step: 0.01, unit: "mm", description: "Doctor blade gap height" },
    "Flow Rate": { min: 5, max: 50, step: 0.5, unit: "ml/min", description: "Slurry flow rate" },
    "Coating Width": { min: 100, max: 500, step: 1, unit: "mm", description: "Coating width" }
  },

  // Drying parameters
  drying: {
    "Web Speed": { min: 0.5, max: 20, step: 0.1, unit: "m/min", description: "Web transport speed" }
  },

  // Calendaring parameters
  calendaring: {
    "Roll Gap": { min: 0.01, max: 0.2, step: 0.001, unit: "mm", description: "Gap between calendar rolls" },
    "Roll Pressure": { min: 10, max: 100, step: 1, unit: "kN/m", description: "Calendaring pressure" },
    "Temperature": { min: 20, max: 150, step: 1, unit: "°C", description: "Roll temperature" },
    "Roll Speed": { min: 0.1, max: 10, step: 0.1, unit: "m/min", description: "Roll speed" },
    "Dry Thickness": { min: 10, max: 200, step: 1, unit: "μm", description: "Dry electrode thickness" },
    "Initial Porosity": { min: 0.1, max: 0.8, step: 0.01, description: "Initial electrode porosity" }
  },

  // Slitting parameters
  slitting: {
    "Blade Sharpness": { min: 0.1, max: 1.0, step: 0.01, description: "Blade sharpness factor" },
    "Slitting Speed": { min: 1, max: 50, step: 0.5, unit: "m/min", description: "Slitting speed" },
    "Target Width": { min: 50, max: 300, step: 1, unit: "mm", description: "Target electrode width" },
    "Slitting Tension": { min: 10, max: 200, step: 1, unit: "N/m", description: "Web tension during slitting" }
  },

  // Electrode Inspection parameters
  inspection: {
    "Epsilon Width Max": { min: 0.01, max: 1.0, step: 0.01, unit: "mm", description: "Maximum width tolerance" },
    "Epsilon Thickness Max": { min: 1, max: 50, step: 1, unit: "μm", description: "Maximum thickness tolerance" },
    "B Max": { min: 0.5, max: 5.0, step: 0.1, description: "Maximum defect factor" },
    "D Surface Max": { min: 1, max: 10, step: 1, description: "Maximum surface defects per cm²" }
  },

  // Rewinding parameters
  rewinding: {
    "Rewinding Speed": { min: 0.1, max: 2.0, step: 0.1, unit: "m/s", description: "Rewinding speed" },
    "Initial Tension": { min: 50, max: 500, step: 10, unit: "N", description: "Initial winding tension" },
    "Tapering Steps": { min: 0.1, max: 1.0, step: 0.05, unit: "m", description: "Tension tapering distance" },
    "Environment Humidity": { min: 10, max: 80, step: 1, unit: "%", description: "Environmental humidity" }
  },

  // Electrolyte Filling parameters
  electrolyte_filling: {
    "Vacuum Level": { min: 10, max: 1000, step: 10, unit: "mbar", description: "Vacuum level" },
    "Vacuum Filling": { min: 50, max: 500, step: 10, unit: "ml/min", description: "Filling rate under vacuum" },
    "Soaking Time": { min: 1, max: 60, step: 1, unit: "minutes", description: "Electrolyte soaking time" }
  },

  // Formation Cycling parameters
  formation_cycling: {
    "Charge Current A": { min: 0.01, max: 1.0, step: 0.01, unit: "A", description: "Formation charging current" },
    "Charge Voltage Limit V": { min: 3.0, max: 4.5, step: 0.01, unit: "V", description: "Maximum charge voltage" },
    "Initial Voltage": { min: 2.5, max: 4.0, step: 0.01, unit: "V", description: "Initial cell voltage" },
    "Formation Duration s": { min: 3600, max: 86400, step: 3600, unit: "seconds", description: "Formation duration" }
  },

  // Aging parameters
  aging: {
    "K Leak": { min: 1e-10, max: 1e-6, step: 1e-10, description: "Leakage coefficient" },
    "Temperature": { min: 15, max: 60, step: 1, unit: "°C", description: "Aging temperature" },
    "Aging Time Days": { min: 1, max: 30, step: 1, unit: "days", description: "Aging duration" }
  }
};

// Function to validate a single parameter value
export const validateParameter = (stageId, fieldName, value) => {
  const stageType = getStageValidationType(stageId);
  const validation = parameterValidation[stageType]?.[fieldName];
  
  if (!validation) {
    return { isValid: true, error: null };
  }

  const numValue = parseFloat(value);
  
  if (isNaN(numValue)) {
    return { isValid: false, error: "Must be a valid number" };
  }

  if (numValue < validation.min) {
    return { 
      isValid: false, 
      error: `Must be ≥ ${validation.min}${validation.unit ? ' ' + validation.unit : ''}` 
    };
  }

  if (numValue > validation.max) {
    return { 
      isValid: false, 
      error: `Must be ≤ ${validation.max}${validation.unit ? ' ' + validation.unit : ''}` 
    };
  }

  return { isValid: true, error: null };
};

// Function to validate all parameters for a stage
export const validateAllParameters = (stageId, inputValues) => {
  const errors = {};
  let isValid = true;

  // Special validation for mixing stages (must sum to 1.0)
  if (stageId.includes("Mixing")) {
    const electrodeType = stageId.includes("Anode") ? "Anode" : "Cathode";
    const mixingFields = [`${electrodeType} AM`, `${electrodeType} CA`, `${electrodeType} PVDF`, `${electrodeType} Solvent`];
    
    let sum = 0;
    const fieldErrors = {};
    
    mixingFields.forEach(field => {
      const value = inputValues[field];
      const validation = validateParameter(stageId, field.split(' ')[1], value); // Extract parameter name
      
      if (!validation.isValid) {
        fieldErrors[field] = validation.error;
        isValid = false;
      } else {
        sum += parseFloat(value || 0);
      }
    });

    // Check if sum equals 1.0
    if (Math.abs(sum - 1.0) > 0.0001 && sum > 0) {
      const sumError = `Total must equal 1.00 (currently ${sum.toFixed(3)})`;
      mixingFields.forEach(field => {
        if (!fieldErrors[field]) {
          fieldErrors[field] = sumError;
        }
      });
      isValid = false;
    }

    Object.assign(errors, fieldErrors);
  } else {
    // Standard validation for other stages
    Object.keys(inputValues).forEach(fieldName => {
      const value = inputValues[fieldName];
      if (value !== undefined && value !== "") {
        const validation = validateParameter(stageId, fieldName, value);
        if (!validation.isValid) {
          errors[fieldName] = validation.error;
          isValid = false;
        }
      }
    });
  }

  return { isValid, errors };
};

// Helper function to get stage validation type
const getStageValidationType = (stageId) => {
  if (stageId.includes("Mixing")) return "mixing";
  if (stageId.includes("Coating")) return "coating";
  if (stageId.includes("Drying")) return "drying";
  if (stageId.includes("Calendaring")) return "calendaring";
  if (stageId.includes("Slitting")) return "slitting";
  if (stageId.includes("Inspection")) return "inspection";
  if (stageId === "Rewinding") return "rewinding";
  if (stageId === "Electrolyte Filling") return "electrolyte_filling";
  if (stageId === "Formation Cycling") return "formation_cycling";
  if (stageId === "Aging") return "aging";
  return null;
};

// Function to get parameter info for display
export const getParameterInfo = (stageId, fieldName) => {
  const stageType = getStageValidationType(stageId);
  
  // Handle mixing parameters specially
  if (stageId.includes("Mixing")) {
    const paramName = fieldName.split(' ')[1]; // Extract "AM" from "Anode AM"
    return parameterValidation.mixing[paramName];
  }
  
  return parameterValidation[stageType]?.[fieldName];
};

// Default parameter values
export const getDefaultParameters = (stageId) => {
  const defaults = {};
  const stageType = getStageValidationType(stageId);
  
  if (stageId.includes("Mixing")) {
    const electrodeType = stageId.includes("Anode") ? "Anode" : "Cathode";
    // Default mixing ratios that sum to 1.0
    defaults[`${electrodeType} AM`] = electrodeType === "Anode" ? "0.7" : "0.6";
    defaults[`${electrodeType} CA`] = "0.1";
    defaults[`${electrodeType} PVDF`] = "0.1";
    defaults[`${electrodeType} Solvent`] = electrodeType === "Anode" ? "0.1" : "0.2";
  } else if (parameterValidation[stageType]) {
    Object.keys(parameterValidation[stageType]).forEach(fieldName => {
      const validation = parameterValidation[stageType][fieldName];
      // Set default to middle of range
      defaults[fieldName] = ((validation.min + validation.max) / 2).toString();
    });
  }
  
  return defaults;
};