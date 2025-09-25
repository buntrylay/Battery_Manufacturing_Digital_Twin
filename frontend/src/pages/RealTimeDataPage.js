import React, { useState } from "react";
import "../styles/RealTimeDataPage.css";
//TODO: Replace with Websocket updates
import { useFlowPage } from "../contexts/FlowPageContext";

function RealTimeDataPage() {
  const { MACHINE_FLOW } = useFlowPage();
  let machineIds = MACHINE_FLOW.map((stage) => stage.id);

  let [selectedMachine, setMachineStage] = useState("Select a Machine");

  let handleMachineChange = (event) => {
    setMachineStage(event.target.value);
  };

  //Conditionally rendering the iframe based on machine selected

  return (
    <div className="realtime-page">
      <h2 className="page-title">Real-Time Data</h2>

      <div className="machine-select">
        <label htmlFor="machine">Select a Machine:</label>
        <select id="machine" onChange={handleMachineChange}>
          <option value="Select a Machine">-- Select a Machine --</option>
          {machineIds.map((selectedMachine) => (
            <option key={selectedMachine.id} value={machineIds.stage}>
              {selectedMachine}
            </option>
          ))}
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
          <p>Displaying real-time data for Anode Mixing machine.</p>
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
          <p>Displaying real-time data for Electro lyte Filling machine.</p>
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
