import React from "react";
import { inputsByStage } from "./constants";

const SidePanel = ({ selectedStage, onClose }) => {
  if (!selectedStage) return null;

  const fields = inputsByStage[selectedStage.id] || [];

  return (
    <div className="card side-panel">
      <div className="side-panel-header">
        <div className="side-title">{selectedStage.id}</div>
        <button className="close-btn" onClick={onClose}>×</button>
      </div>

      <div className="side-grid">
        {fields.map((f) => (
          <label key={f} className="side-field">
            <span>{f}</span>
            <input type="number" placeholder="Enter value..." />
          </label>
        ))}
      </div>
    </div>
  );
};

export default SidePanel;
