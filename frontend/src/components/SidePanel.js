import React, { useState, useEffect, useMemo } from "react";
import { inputsByStage, convertInputsToParameters } from "./constants";
import { 
  validateAllParameters, 
  validateParameter, 
  getParameterInfo, 
  getDefaultParameters 
} from "./parameterValidation";

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
    let initialValues = {};

    if (isMixingStage) {
      // Load mixing inputs
      const savedInputs = localStorage.getItem(`mixingInputs_${selectedStage.id}`);
      if (savedInputs) {
        try {
          const savedData = JSON.parse(savedInputs);
          const electrodeType = selectedStage.id.includes("Anode")
            ? "Anode"
            : "Cathode";

          // Map saved data back to input field format
          initialValues = {
            [`${electrodeType} PVDF`]: savedData.PVDF || "",
            [`${electrodeType} CA`]: savedData.CA || "",
            [`${electrodeType} AM`]: savedData.AM || "",
            [`${electrodeType} Solvent`]: savedData.Solvent || "",
          };
          setStatus("Previously saved inputs loaded");
        } catch (error) {
          console.error("Error loading saved mixing inputs:", error);
          fields.forEach((field) => {
            initialValues[field] = "";
          });
        }
      } else {
        fields.forEach((field) => {
          initialValues[field] = "";
        });
        setStatus("");
      }
    } else {
      // Load inputs for other machine types
      const savedInputs = localStorage.getItem(`machineInputs_${selectedStage.id}`);
      if (savedInputs) {
        try {
          const savedData = JSON.parse(savedInputs);
          initialValues = savedData.inputValues || {};
          setStatus("Previously saved inputs loaded");
        } catch (error) {
          console.error("Error loading saved machine inputs:", error);
          fields.forEach((field) => {
            initialValues[field] = "";
          });
        }
      } else {
        fields.forEach((field) => {
          initialValues[field] = "";
        });
        setStatus("");
      }
    }

    setInputValues(initialValues);
  }, [selectedStage, fields, isMixingStage]);

  if (!selectedStage) return null;

  const handleInputChange = (field, value) => {
    setInputValues((prev) => ({
      ...prev,
      [field]: value,
    }));

    // Real-time validation
    if (selectedStage && value !== "") {
      let validation;
      if (selectedStage.id.includes("Mixing")) {
        const paramName = field.split(' ')[1]; // Extract "AM" from "Anode AM"
        validation = validateParameter(selectedStage.id, paramName, value);
      } else {
        validation = validateParameter(selectedStage.id, field, value);
      }

      setValidationErrors((prev) => ({
        ...prev,
        [field]: validation.isValid ? null : validation.error,
      }));
    } else {
      // Clear validation error when field is empty
      setValidationErrors((prev) => ({
        ...prev,
        [field]: null,
      }));
    }
  };



  const handleSaveInputs = () => {
    try {
      // Validate all inputs before saving
      const validation = validateAllParameters(selectedStage.id, inputValues);
      
      if (!validation.isValid) {
        setValidationErrors(validation.errors);
        setStatus("Please fix validation errors before saving");
        return;
      }

      if (isMixingStage) {
        const electrodeType = selectedStage.id.includes("Anode")
          ? "Anode"
          : "Cathode";

        // Save mixing data
        const savedData = {
          stage: selectedStage.id,
          electrode_type: electrodeType,
          PVDF: parseFloat(inputValues[`${electrodeType} PVDF`] || 0),
          CA: parseFloat(inputValues[`${electrodeType} CA`] || 0),
          AM: parseFloat(inputValues[`${electrodeType} AM`] || 0),
          Solvent: parseFloat(inputValues[`${electrodeType} Solvent`] || 0),
          timestamp: new Date().toISOString(),
        };

        localStorage.setItem(
          `mixingInputs_${selectedStage.id}`,
          JSON.stringify(savedData)
        );
        setStatus(`Inputs saved for ${electrodeType} mixing`);
      } else {
        // Save inputs for other machine types
        const savedData = {
          stage: selectedStage.id,
          inputValues: inputValues,
          timestamp: new Date().toISOString(),
        };

        localStorage.setItem(
          `machineInputs_${selectedStage.id}`,
          JSON.stringify(savedData)
        );
        setStatus(`Inputs saved for ${selectedStage.id}`);
      }

      // Clear validation errors after successful save
      setValidationErrors({});
    } catch (error) {
      setStatus("Error saving inputs: " + error.message);
    }
  };

  const currentSum = isMixingStage
    ? Object.values(inputValues).reduce(
        (acc, val) => acc + parseFloat(val || 0),
        0
      )
    : 0;

  // Preset management functions
  const loadDefaultPreset = () => {
    const defaults = getDefaultParameters(selectedStage.id);
    setInputValues(defaults);
    setValidationErrors({});
    setStatus("Default parameters loaded");
  };

  const saveAsPreset = () => {
    const presetName = prompt("Enter a name for this preset:");
    if (presetName && presetName.trim()) {
      const presets = JSON.parse(localStorage.getItem(`presets_${selectedStage.id}`) || "{}");
      presets[presetName.trim()] = {
        inputValues: inputValues,
        timestamp: new Date().toISOString(),
      };
      localStorage.setItem(`presets_${selectedStage.id}`, JSON.stringify(presets));
      setStatus(`Preset "${presetName}" saved`);
    }
  };

  const loadPreset = (presetName) => {
    const presets = JSON.parse(localStorage.getItem(`presets_${selectedStage.id}`) || "{}");
    if (presets[presetName]) {
      setInputValues(presets[presetName].inputValues);
      setValidationErrors({});
      setStatus(`Preset "${presetName}" loaded`);
    }
    setShowPresetMenu(false);
  };

  const getAvailablePresets = () => {
    return JSON.parse(localStorage.getItem(`presets_${selectedStage.id}`) || "{}");
  };

  const deletePreset = (presetName) => {
    const presets = JSON.parse(localStorage.getItem(`presets_${selectedStage.id}`) || "{}");
    delete presets[presetName];
    localStorage.setItem(`presets_${selectedStage.id}`, JSON.stringify(presets));
    setStatus(`Preset "${presetName}" deleted`);
  };

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
          <div className="side-panel-content">
            <div className="side-grid">
            {fields.map((f) => {
              const paramInfo = getParameterInfo(selectedStage.id, f);
              const hasError = validationErrors[f];
              
              return (
                <label key={f} className={`side-field ${hasError ? 'error' : ''}`}>
                  <div className="field-header">
                    <span className="field-name">{f}</span>
                    {paramInfo?.unit && <span className="field-unit">({paramInfo.unit})</span>}
                  </div>
                  <input
                    type="number"
                    step={paramInfo?.step || "0.01"}
                    min={paramInfo?.min || "0"}
                    max={paramInfo?.max || (isMixingStage ? "1" : undefined)}
                    placeholder={paramInfo ? `${paramInfo.min}-${paramInfo.max}` : "Enter value..."}
                    value={inputValues[f] || ""}
                    onChange={(e) => handleInputChange(f, e.target.value)}
                    className={hasError ? 'input-error' : ''}
                  />
                  {hasError && <div className="error-message">{hasError}</div>}
                  {paramInfo?.description && !hasError && (
                    <div className="field-description">{paramInfo.description}</div>
                  )}
                </label>
              );
            })}
          </div>

          <div className="machine-controls">
            {isMixingStage && (
              <div className="ratio-sum">
                <span>Total: {currentSum.toFixed(3)}</span>
                {Math.abs(currentSum - 1) > 0.0001 && currentSum > 0 && (
                  <span className="error-text"> (Must equal 1.00)</span>
                )}
              </div>
            )}
            
            {/* Preset Management */}
            <div className="preset-controls">
              <div className="preset-buttons">
                <button onClick={loadDefaultPreset} className="preset-btn default-btn">
                  Defaults
                </button>
                <button onClick={saveAsPreset} className="preset-btn save-preset-btn">
                  Save Preset
                </button>
                <button 
                  onClick={() => setShowPresetMenu(!showPresetMenu)} 
                  className="preset-btn load-preset-btn"
                >
                  Load Preset
                </button>
              </div>
              
              {showPresetMenu && (
                <div className="preset-menu">
                  {Object.keys(getAvailablePresets()).length === 0 ? (
                    <div className="no-presets">No saved presets</div>
                  ) : (
                    Object.keys(getAvailablePresets()).map(presetName => (
                      <div key={presetName} className="preset-item">
                        <span onClick={() => loadPreset(presetName)} className="preset-name">
                          {presetName}
                        </span>
                        <button 
                          onClick={() => deletePreset(presetName)} 
                          className="delete-preset-btn"
                        >
                          Delete
                        </button>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
            
            <div className="control-buttons">
              <button onClick={handleSaveInputs} className="save-inputs-btn">
                Save Parameters
              </button>
            </div>
            
            <div className="simulation-info">
              <small>Parameters saved! Use "Start Full Simulation" above to run the complete battery manufacturing process.</small>
            </div>
            
            {status && <div className={`status-message ${status.includes('❌') ? 'error' : status.includes('✅') ? 'success' : ''}`}>{status}</div>}
          </div>
          </div>
        </>
      ) : null}
    </div>
  );
};

export default SidePanel;
