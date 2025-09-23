import React, { useState } from "react";
import "../styles/RealTimeDataPage.css";

function RealTimeDataPage() {
  const [selectedMachine, setSelectedMachine] = useState("Mixing (Cathode)");

  //Conditionally rendering the iframe based on machine selected

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
        <h3>Live Data Visualization for {selectedMachine}</h3>
        {selectedMachine === "Cathode Mixing" && (
          <p>Displaying real-time data for Cathode Mixing machine.</p>
        )}
        {selectedMachine === "Cathode Coating" && (
          <p>Displaying real-time data for Cathode Coating machine.</p>
        )}
        {selectedMachine === "Cathode Drying" && (
          <p>Displaying real-time data for Cathode Drying machine.</p>
        )}
        {selectedMachine === "Cathode Calendaring" && (
          <p>Displaying real-time data for Cathode Calendaring machine.</p>
        )}
        {selectedMachine === "Cathode Slitting" && (
          <p>Displaying real-time data for Cathode Slitting machine.</p>
        )}
        {selectedMachine === "Cathode Inspection" && (
          <p>Displaying real-time data for Cathode Inspection machine.</p>
        )}
        {selectedMachine === "Anode Mixing" && (
          <p>Displaying real-time data for Anode  Mixing machine.</p>
        )}
        {selectedMachine === "Anode Coating" && (
          <p>Displaying real-time data for Anode Coating machine.</p>
        )}
        {selectedMachine === "Anode Drying" && (
          <p>Displaying real-time data for Anode Drying machine.</p>
        )}
        {selectedMachine === "Anode Calendaring" && (
          <p>Displaying real-time data for Anode Calendaring machine.</p>
        )}
        {selectedMachine === "Anode Slitting" && (
          <p>Displaying real-time data for Anode Slitting machine.</p>
        )}
        {selectedMachine === "Anode Inspection" && (
          <p>Displaying real-time data for Anode Inspection machine.</p>
        )}
        {selectedMachine === "Rewinding" && (
          <p>Displaying real-time data for Rewinding machine.</p>
        )}
        {selectedMachine === "Electrolyte Filling" && (
          <p>Displaying real-time data for Electro  lyte Filling machine.</p>
        )}
        {selectedMachine === "Formation Cycling" && (
          <p>Displaying real-time data for Formation Cycling machine.</p>
        )}
        {selectedMachine === "Aging" && (
          <p>Displaying real-time data for Aging machine.</p>
        )} 
      </div>
     
    </div>
  );
}

export default RealTimeDataPage;
