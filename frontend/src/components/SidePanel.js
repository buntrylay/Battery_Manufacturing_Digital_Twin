import React from "react";
import { inputsByStage } from "./constants";

const SidePanel = ({ selectedStage }) => {
  if (!selectedStage) {
    return (
      <div className="side-panel-hint">Click a stage to view/edit inputs.</div>
    );
  }

  const fields = inputsByStage[selectedStage.id] || [];

  return (
    <div className="card side-panel">
      <div className="side-title">{selectedStage.label}</div>

      <h4>Anode {selectedStage.label}</h4>
      <div className="side-grid">
        {fields.map((f) => (
          <label key={"anode-" + f} className="side-field">
            <span>{f}</span>
            <input type="number" placeholder="Enter value..." />
          </label>
        ))}
      </div>

      <h4>Cathode {selectedStage.label}</h4>
      <div className="side-grid">
        {fields.map((f) => (
          <label key={"cathode-" + f} className="side-field">
            <span>{f}</span>
            <input type="number" placeholder="Enter value..." />
          </label>
        ))}
      </div>
    </div>
  );
};

export default SidePanel;
