import React, { useState, useEffect, useMemo } from "react";
import { inputsByStage, stageDescriptions, parameterUnits } from "./constants";
import {
  validateParameters,
  updateParameters,
  getCurrentParameters,
} from "../services/api";

const SidePanel = ({ selectedStage, onClose, isOpen }) => {
  const [inputValues, setInputValues] = useState({});
  const [status, setStatus] = useState("");
  // Get fields and stage info before any early returns
  const fields = useMemo(() => {
    return selectedStage ? inputsByStage[selectedStage.id] || [] : [];
  }, [selectedStage]);

  const isMixingStage = selectedStage
    ? selectedStage.id === "Anode Mixing" ||
      selectedStage.id === "Cathode Mixing"
    : false;

  // Initialize input values when stage changes
  useEffect(() => {
    // Try to load previously saved inputs (new format first, then legacy mixing format)
    const savedInputs =
      localStorage.getItem(`machineInputs_${selectedStage.id}`) ||
      (isMixingStage
        ? localStorage.getItem(`mixingInputs_${selectedStage.id}`)
        : null);
    let initialValues = {};

    if (savedInputs) {
      try {
        const savedData = JSON.parse(savedInputs);

        if (savedData.parameters) {
          // New format - direct parameter mapping
          Object.keys(savedData.parameters).forEach((field) => {
            if (fields.includes(field)) {
              initialValues[field] = savedData.parameters[field].toString();
            }
          });
        } else if (isMixingStage && savedData.PVDF !== undefined) {
          // Legacy mixing format
          const electrodeType = selectedStage.id.includes("Anode")
            ? "Anode"
            : "Cathode";
          initialValues = {
            [`${electrodeType} PVDF`]: savedData.PVDF || "",
            [`${electrodeType} CA`]: savedData.CA || "",
            [`${electrodeType} AM`]: savedData.AM || "",
            [`${electrodeType} Solvent`]: savedData.Solvent || "",
          };
        }

        // Fill in any missing fields with empty values
        fields.forEach((field) => {
          if (!(field in initialValues)) {
            initialValues[field] = "";
          }
        });

        setStatus("Previously saved inputs loaded");
      } catch (error) {
        console.error("Error loading saved inputs:", error);
        fields.forEach((field) => {
          initialValues[field] = "";
        });
        setStatus("");
      }
    } else {
      // Initialize with empty values
      fields.forEach((field) => {
        initialValues[field] = "";
      });
      setStatus("");
    }

    setInputValues(initialValues);
  }, [selectedStage, fields, isMixingStage]);

  if (!selectedStage) return null;

  const handleInputChange = (field, value) => {
    setInputValues((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const validateMixingInputs = () => {
    if (!isMixingStage) return true;

    const values = Object.values(inputValues);
    const sum = values.reduce((acc, val) => acc + parseFloat(val || 0), 0);
    return Math.abs(sum - 1) <= 0.0001;
  };

  const hasRequiredInputs = () => {
    // Check if at least some inputs are provided
    return Object.values(inputValues).some(
      (value) => value !== "" && !isNaN(parseFloat(value))
    );
  };



  const handleSaveInputs = async () => {
    // Validate mixing inputs if it's a mixing stage
    if (isMixingStage && !validateMixingInputs()) {
      setStatus("❌ Error: Mixing ratios must total exactly 1.00");
      return;
    }

    // Check if we have any inputs to save
    if (!hasRequiredInputs()) {
      setStatus("❌ Please enter at least one parameter value");
      return;
    }

    try {
      setStatus("Updating machine parameters...");

      // Convert input values to numbers
      const parametersToUpdate = {};
      Object.keys(inputValues).forEach((field) => {
        if (
          inputValues[field] !== "" &&
          !isNaN(parseFloat(inputValues[field]))
        ) {
          parametersToUpdate[field] = parseFloat(inputValues[field]);
        }
      });

      // Check if we have any parameters to update
      if (Object.keys(parametersToUpdate).length === 0) {
        setStatus("❌ Please enter at least one parameter value");
        return;
      }

      // First validate the parameters
      const validationResponse = await validateParameters(
        selectedStage.id,
        parametersToUpdate
      );

      // Check if validation succeeded
      if (!validationResponse.data?.success) {
        const errorMsg = validationResponse.data?.message || 
                        validationResponse.data?.errors || 
                        'Unknown validation error';
        setStatus(`❌ Validation failed: ${errorMsg}`);
        return;
      }
      
      // Additional check for the 'valid' field in the data
      if (validationResponse.data?.data && !validationResponse.data.data.valid) {
        const errorMsg = validationResponse.data.data.error || 
                        validationResponse.data.message || 
                        'Parameters are invalid';
        setStatus(`❌ Validation failed: ${errorMsg}`);
        return;
      }

      // If validation passes, update the parameters
      const updateResponse = await updateParameters(
        selectedStage.id,
        parametersToUpdate
      );

      if (updateResponse.data.message) {
        setStatus(`✓ ${updateResponse.data.message}`);

        // Save to localStorage for persistence
        localStorage.setItem(
          `machineInputs_${selectedStage.id}`,
          JSON.stringify({
            stage: selectedStage.id,
            parameters: parametersToUpdate,
            timestamp: new Date().toISOString(),
          })
        );

        // Clear any previous mixing-specific saves
        if (isMixingStage) {
          localStorage.removeItem(`mixingInputs_${selectedStage.id}`);
        }
      }
    } catch (error) {
      console.error("Parameter update error:", error);
      if (error.response?.status === 409) {
        setStatus("❌ Machine is busy. Please try again later.");
      } else if (error.response?.status === 400) {
        setStatus(
          `❌ Invalid parameters: ${
            error.response?.data?.detail || error.message
          }`
        );
      } else {
        setStatus(
          `❌ Update failed: ${error.response?.data?.detail || error.message}`
        );
      }
    }
  };

  const handleLoadCurrentParameters = async () => {
    try {
      setStatus("Loading current parameters...");

      const response = await getCurrentParameters(selectedStage.id);
      const currentParams = response.data.data?.parameters || {};

      // Map backend parameters to frontend field names
      const newInputValues = {};
      fields.forEach((field) => {
        newInputValues[field] = "";
      });

      // Create comprehensive parameter mapping
      const mapParameters = (params, mappings) => {
        Object.entries(mappings).forEach(([frontendField, backendField]) => {
          if (params[backendField] !== undefined) {
            newInputValues[frontendField] = params[backendField].toString();
          }
        });
      };

      // Define parameter mappings for each machine type
      if (isMixingStage) {
        const electrodeType = selectedStage.id.includes("Anode")
          ? "Anode"
          : "Cathode";
        mapParameters(currentParams, {
          [`${electrodeType} PVDF`]: "PVDF_ratio",
          [`${electrodeType} CA`]: "CA_ratio",
          [`${electrodeType} AM`]: "AM_ratio",
          [`${electrodeType} Solvent`]: "solvent_ratio",
        });
      } else if (selectedStage.id.includes("Coating")) {
        mapParameters(currentParams, {
          "Coating Speed": "coating_speed",
          "Gap Height": "gap_height",
          "Flow Rate": "flow_rate",
          "Coating Width": "coating_width",
        });
      } else if (selectedStage.id.includes("Drying")) {
        mapParameters(currentParams, {
          "Web Speed": "web_speed",
        });
      } else if (selectedStage.id.includes("Calendaring")) {
        mapParameters(currentParams, {
          "Roll Gap": "roll_gap",
          "Roll Pressure": "roll_pressure",
          Temperature: "temperature",
          "Roll Speed": "roll_speed",
          "Dry Thickness": "dry_thickness",
          "Initial Porosity": "initial_porosity",
        });
      } else if (selectedStage.id.includes("Slitting")) {
        mapParameters(currentParams, {
          "Blade Sharpness": "blade_sharpness",
          "Slitting Speed": "slitting_speed",
          "Target Width": "target_width",
          "Slitting Tension": "slitting_tension",
        });
      } else if (selectedStage.id.includes("Inspection")) {
        mapParameters(currentParams, {
          "Width Tolerance": "epsilon_width_max",
          "Thickness Tolerance": "epsilon_thickness_max",
          "B Max": "B_max",
          "Defects Allowed": "D_surface_max",
        });
      } else if (selectedStage.id === "Rewinding") {
        mapParameters(currentParams, {
          "Rewinding Speed": "rewinding_speed",
          "Initial Tension": "initial_tension",
          "Tapering Steps": "tapering_steps",
          "Environment Humidity": "environment_humidity",
        });
      } else if (selectedStage.id === "Electrolyte Filling") {
        mapParameters(currentParams, {
          "Vacuum Level": "vacuum_level",
          "Vacuum Filling": "vacuum_filling",
          "Soaking Time": "soaking_time",
        });
      } else if (selectedStage.id === "Formation Cycling") {
        mapParameters(currentParams, {
          "Charge Current": "charge_current_A",
          Voltage: "charge_voltage_limit_V",
          "Initial Voltage": "initial_voltage",
        });
      } else if (selectedStage.id === "Aging") {
        mapParameters(currentParams, {
          "Leak Rate": "k_leak",
          Temperature: "temperature",
          "Aging Days": "aging_time_days",
        });
      }

      setInputValues(newInputValues);
      setStatus(
        `✓ Loaded current parameters (Machine state: ${response.data.data?.status?.state || 'Unknown'})`
      );
    } catch (error) {
      console.error("Load parameters error:", error);
      setStatus(
        `❌ Failed to load parameters: ${
          error.response?.data?.detail || error.message
        }`
      );
    }
  };

  const currentSum = isMixingStage
    ? Object.values(inputValues).reduce(
        (acc, val) => acc + parseFloat(val || 0),
        0
      )
    : 0;

  return (
    <div
      className={`card side-panel${isOpen ? " open" : ""}${
        !selectedStage ? " hidden" : ""
      }`}
    >
      {selectedStage ? (
        <>
          <div className="side-panel-header">
            <div className="side-title">{selectedStage.id}</div>
            <button className="close-btn" onClick={onClose}>
              ×
            </button>
          </div>
          <div className="side-grid">
            {fields.map((f) => {
              // Determine input constraints based on field type
              let inputProps = {
                type: "number",
                step: "0.01",
                min: "0",
                placeholder: "Enter value...",
              };

              // Set appropriate max values and steps for different parameter types
              if (isMixingStage) {
                inputProps.max = "1";
                inputProps.step = "0.001";
              } else if (f.includes("Temperature")) {
                inputProps.max = "200";
                inputProps.step = "1";
              } else if (f.includes("Pressure")) {
                inputProps.max = "10000000";
                inputProps.step = "100000";
              } else if (f.includes("Speed")) {
                inputProps.max = "10";
                inputProps.step = "0.01";
              } else if (f.includes("Humidity")) {
                inputProps.max = "100";
                inputProps.step = "1";
              } else if (f.includes("Voltage")) {
                inputProps.max = "5";
                inputProps.step = "0.1";
              } else if (f.includes("Current")) {
                inputProps.max = "1";
                inputProps.step = "0.01";
              } else {
                // Remove max constraint for other parameters
                delete inputProps.max;
              }

              const unit = parameterUnits[f] || "";
              
              return (
                <label key={f} className="side-field">
                  <span className="parameter-label">
                    {f}
                    {unit && <span className="parameter-unit">({unit})</span>}
                  </span>
                  <input
                    {...inputProps}
                    value={inputValues[f] || ""}
                    onChange={(e) => handleInputChange(f, e.target.value)}
                    placeholder={unit ? `Enter value in ${unit}` : "Enter value"}
                  />
                </label>
              );
            })}
          </div>

          <div className="parameter-controls">
            {isMixingStage && (
              <div className="ratio-sum">
                <span>Total: {currentSum.toFixed(3)}</span>
                {Math.abs(currentSum - 1) > 0.0001 && currentSum > 0 && (
                  <span className="error-text"> (Must equal 1.00)</span>
                )}
              </div>
            )}

            <div className="stage-info">
              <small className="stage-description">
                {stageDescriptions[selectedStage.id] ||
                  "Configure machine parameters"}
              </small>
            </div>

            <div className="control-buttons">
              <button
                onClick={handleLoadCurrentParameters}
                className="load-params-btn"
                title="Load current machine parameters"
              >
                Load Current
              </button>

              <button
                onClick={handleSaveInputs}
                className="save-inputs-btn"
                title="Apply changes to machine"
                disabled={!hasRequiredInputs()}
              >
                Apply Changes
              </button>
            </div>

            {status && <div className="status-message">{status}</div>}
          </div>
        </>
      ) : (
        <div className="no-selection">
          <p>Please select a machine to configure its parameters.</p>
        </div>
      )}
    </div>
  );
};

export default SidePanel;
