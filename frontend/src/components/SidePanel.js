import React, { useState, useEffect, useMemo } from "react";
import {
  inputsByStage,
  stageDescriptions,
  getDefaultParameters,
} from "./constants";
import {
  validateParameters,
  updateParameters,
  getCurrentParameters,
} from "../services/api";

const SidePanel = ({ selectedStage, onClose, isOpen }) => {
  const [inputValues, setInputValues] = useState({});
  const [status, setStatus] = useState("");
  const [validationErrors, setValidationErrors] = useState({});
  const [showPresetMenu, setShowPresetMenu] = useState(false);
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
    if (!selectedStage) return;

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
          // Legacy mixing format from the older component version
          const electrodeType = selectedStage.id.includes("Anode")
            ? "Anode"
            : "Cathode";
          initialValues = {
            [`${electrodeType} PVDF`]: savedData.PVDF || "",
            [`${electrodeType} CA`]: savedData.CA || "",
            [`${electrodeType} AM`]: savedData.AM || "",
            [`${electrodeType} Solvent`]: savedData.Solvent || "",
          };
        } else if (savedData.inputValues) {
          // A different legacy format that might exist
          initialValues = savedData.inputValues || {};
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
      // No saved data found, initialize with empty values
      fields.forEach((field) => {
        initialValues[field] = "";
      });
      setStatus("");
    }

    setInputValues(initialValues);
    setValidationErrors({});
  }, [selectedStage, fields, isMixingStage]);

  if (!selectedStage) return null;

  const handleInputChange = (field, value) => {
    setInputValues((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const hasRequiredInputs = () => {
    // Check if at least some inputs are provided
    return Object.values(inputValues).some(
      (value) => value !== "" && !isNaN(parseFloat(value))
    );
  };

  const handleValidateInputs = async () => {
    try {
      setStatus("Validating parameters...");

      // Convert input values to numbers for validation
      const parametersToValidate = {};
      Object.keys(inputValues).forEach((field) => {
        if (inputValues[field] !== "") {
          parametersToValidate[field] = parseFloat(inputValues[field]);
        }
      });

      const response = await validateParameters(
        selectedStage.id,
        parametersToValidate
      );

      if (response.data.valid) {
        setStatus("✓ Parameters are valid and ready to apply");
      } else {
        setStatus(`❌ Validation failed: ${response.data.error}`);
      }
    } catch (error) {
      console.error("Parameter validation error:", error);
      setStatus(
        `❌ Validation error: ${error.response?.data?.detail || error.message}`
      );
    }
  };

  const handleApplyChanges = async () => {
    // Check if we have any inputs to save
    if (!hasRequiredInputs()) {
      setStatus("❌ Please enter at least one parameter value");
      return;
    }

    try {
      setStatus("Applying changes to machine...");

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

      // First validate the parameters (best practice)
      const validationResponse = await validateParameters(
        selectedStage.id,
        parametersToUpdate
      );

      if (!validationResponse.data.valid) {
        setStatus(`❌ Validation failed: ${validationResponse.data.error}`);
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

        // Clear any previous legacy mixing saves to avoid conflicts
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
      const currentParams = response.data.parameters;

      // Initialize all fields to empty strings first
      const newInputValues = {};
      fields.forEach((field) => {
        newInputValues[field] = "";
      });

      // Map backend parameters to frontend field names
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
      } // ... add other 'else if' blocks for all other stages here ...

      setInputValues(newInputValues);
      setStatus(
        `✓ Loaded current parameters (Machine state: ${response.data.machine_state})`
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

  // Preset management functions would go here if needed (saveAsPreset, loadPreset, etc.)

  return (
    <div className={`side-panel ${isOpen ? "open" : ""}`}>
      <div className="side-panel-header">
        <div className="side-title">{selectedStage.id}</div>
        <button className="close-btn" onClick={onClose}>
          ×
        </button>
      </div>

      <div className="side-grid">
        {fields.map((f) => {
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
          } else if (f.includes("Humidity")) {
            inputProps.max = "100";
            inputProps.step = "1";
          } else if (f.includes("Voltage")) {
            inputProps.max = "5";
            inputProps.step = "0.1";
          } else if (f.includes("Current")) {
            inputProps.max = "1";
          } else {
            delete inputProps.max; // No max for other parameters
          }

          return (
            <label key={f} className="side-field">
              <span>{f}</span>
              <input
                {...inputProps}
                value={inputValues[f] || ""}
                onChange={(e) => handleInputChange(f, e.target.value)}
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
            onClick={handleValidateInputs}
            className="validate-btn"
            title="Validate parameter values"
            disabled={!hasRequiredInputs()}
          >
            Validate
          </button>

          <button
            onClick={handleApplyChanges}
            className="save-inputs-btn"
            title="Apply changes to machine"
            disabled={!hasRequiredInputs()}
          >
            Apply Changes
          </button>
        </div>

        {status && <div className="status-message">{status}</div>}
      </div>
    </div>
  );
};

export default SidePanel;
