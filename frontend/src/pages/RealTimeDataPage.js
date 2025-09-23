import React, { useState } from "react";
import "../styles/RealTimeDataPage.css";

function RealTimeDataPage() {
  const [selectedMachine, setSelectedMachine] = useState("Mixing (Cathode)");

  return (
    <div className="realtime-page">
      <h2 className="page-title">Real-Time Data</h2>

      <div className="machine-select">
        <label htmlFor="machine">Select a Machine:</label>
        <select
          id="machine"
          value={selectedMachine}
          onChange={(e) => setSelectedMachine(e.target.value)}
        >
          {/* Cathode Line */}
          <optgroup label="Cathode Line">
            <option value="Cathode Mixing">Mixing (Cathode)</option>
            <option value="Cathode Coating">Coating (Cathode)</option>
            <option value="Cathode Drying">Drying (Cathode)</option>
            <option value="Cathode Calendaring">Calendaring (Cathode)</option>
            <option value="Cathode Slitting">Slitting (Cathode)</option>
            <option value="Cathode Inspection">Inspection (Cathode)</option>
          </optgroup>

          {/* Anode Line */}
          <optgroup label="Anode Line">
            <option value="Anode Mixing">Mixing (Anode)</option>
            <option value="Anode Coating">Coating (Anode)</option>
            <option value="Anode Drying">Drying (Anode)</option>
            <option value="Anode Calendaring">Calendaring (Anode)</option>
            <option value="Anode Slitting">Slitting (Anode)</option>
            <option value="Anode Inspection">Inspection (Anode)</option>
          </optgroup>

          {/* Shared Stages */}
          <optgroup label="Cell Assembly & Aging">
            <option value="Rewinding">Rewinding</option>
            <option value="Electrolyte Filling">Electrolyte Filling</option>
            <option value="Formation Cycling">Formation Cycling</option>
            <option value="Aging">Aging</option>
          </optgroup>
        </select>
      </div>

      <div className="data-grid">
        <div className="data-card">
          <h3>Machine Status</h3>
          <div className="placeholder"></div>
        </div>

        <div className="data-card">
          <h3>Current Batch</h3>
          <div className="placeholder"></div>
        </div>

        <div className="data-card">
          <h3>Sensor Information</h3>
          <div className="placeholder"></div>
        </div>

        <div className="data-card">
          <h3>Sensor Information</h3>
          <div className="placeholder"></div>
        </div>
      </div>
      <div>
        <iframe
          title="Real-Time Data Visualization"
          src="http://localhost:3001"
          style={{ width: "100%", height: "600px", border: "none" }}
        ></iframe>
      </div>
    </div>
  );
}

export default RealTimeDataPage;
