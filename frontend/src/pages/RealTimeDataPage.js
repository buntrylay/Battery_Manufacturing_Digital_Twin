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
      <div>
        <h3>Live Data Visualization for {selectedMachine}</h3>
        {selectedMachine === "Cathode Mixing" && (
          <div className="data-grid">
            <div className="data-card">
              <h3>Machine Status</h3>
              <div className="placeholder">
                <iframe
                  title="Cathode Mixing Live Data"
                  width="100%"
                  height="300"
                  src="http://localhost:3001/public-dashboards/c40861f4fda2438e8b27c0590fdcb0c6"
                ></iframe>
              </div>
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
        )}
        {selectedMachine === "Cathode Coating" && (
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
        )}
        {selectedMachine === "Cathode Drying" && (
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
        )}
        {selectedMachine === "Cathode Calendaring" && (
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
        )}
        {selectedMachine === "Cathode Slitting" && (
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
        )}
        {selectedMachine === "Cathode Inspection" && (
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
        )}
        {selectedMachine === "Anode Mixing" && (
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
        )}
        {selectedMachine === "Anode Coating" && (
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
        )}
        {selectedMachine === "Anode Drying" && (
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
        )}
        {selectedMachine === "Anode Calendaring" && (
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
        )}
        {selectedMachine === "Anode Slitting" && (
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
        )}
        {selectedMachine === "Anode Inspection" && (
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
        )}
        {selectedMachine === "Rewinding" && (
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
        )}
        {selectedMachine === "Electrolyte Filling" && (
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
        )}
        {selectedMachine === "Formation Cycling" && (
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
        )}
        {selectedMachine === "Aging" && (
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
        )}
      </div>
    </div>
  );
}

export default RealTimeDataPage;
