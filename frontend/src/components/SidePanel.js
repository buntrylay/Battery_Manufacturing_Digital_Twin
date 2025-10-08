import React, { useState, useEffect, useMemo } from "react";
import { inputsByStage } from "./constants";

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
    // Try to load previously saved inputs
    const savedInputs = localStorage.getItem(
      `mixingInputs_${selectedStage.id}`
    );
    let initialValues = {};

    if (savedInputs && isMixingStage) {
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
        console.error("Error loading saved inputs:", error);
        fields.forEach((field) => {
          initialValues[field] = "";
        });
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

  const handleSaveInputs = () => {
    if (!isMixingStage) {
      setStatus("This stage doesn't support input saving yet");
      return;
    }

    if (!validateMixingInputs()) {
      setStatus("Error: Input values must total exactly 1.00");
      return;
    }

    try {
      const electrodeType = selectedStage.id.includes("Anode")
        ? "Anode"
        : "Cathode";

      // Save to localStorage for now - later this can be sent to a global state or context
      const savedData = {
        stage: selectedStage.id,
        electrode_type: electrodeType,
        PVDF: parseFloat(inputValues[`${electrodeType} PVDF`] || 0),
        CA: parseFloat(inputValues[`${electrodeType} CA`] || 0),
        AM: parseFloat(inputValues[`${electrodeType} AM`] || 0),
        Solvent: parseFloat(inputValues[`${electrodeType} Solvent`] || 0),
        timestamp: new Date().toISOString(),
      };

      // Store in localStorage with the stage name as key
      localStorage.setItem(
        `mixingInputs_${selectedStage.id}`,
        JSON.stringify(savedData)
      );
      setStatus(`Inputs saved for ${electrodeType} mixing`);
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
            {fields.map((f) => (
              <label key={f} className="side-field">
                <span>{f}</span>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  placeholder="Enter value..."
                  value={inputValues[f] || ""}
                  onChange={(e) => handleInputChange(f, e.target.value)}
                />
              </label>
            ))}
          </div>

          {isMixingStage && (
            <div className="mixing-controls">
              <div className="ratio-sum">
                <span>Total: {currentSum.toFixed(3)}</span>
                {Math.abs(currentSum - 1) > 0.0001 && currentSum > 0 && (
                  <span className="error-text"> (Must equal 1.00)</span>
                )}
              </div>
              <button onClick={handleSaveInputs} className="save-inputs-btn">
                Save Inputs
              </button>
              {status && <div className="status-message">{status}</div>}
            </div>
          )}
        </>
      ) : null}
    </div>
  );
};

export default SidePanel;
