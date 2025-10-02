import React, { useState } from "react";
import "../styles/RealTimeDataPage.css";
//TODO: Replace with Websocket updates
import { useFlowPage } from "../contexts/FlowPageContext";
import { GrafanaMachineDisplay } from "../components/GrafanaMachineDisplay";
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
          <GrafanaMachineDisplay
            url={
              "http://localhost:3001/public-dashboards/c40861f4fda2438e8b27c0590fdcb0c6"
            }
            name="Cathode Mixing"
          />
        )}
        {selectedMachine === "Cathode Coating" && (
          <GrafanaMachineDisplay
            url={
              "http://localhost:3001/public-dashboards/c40861f4fda2438e8b27c0590fdcb0c6"
            }
            name="Cathode Mixing"
          />
        )}
        {selectedMachine === "Cathode Drying" && (
          <GrafanaMachineDisplay
            url={
              "http://localhost:3001/public-dashboards/c40861f4fda2438e8b27c0590fdcb0c6"
            }
            name="Cathode Mixing"
          />
        )}
        {selectedMachine === "Cathode Calendaring" && (
          <GrafanaMachineDisplay
            url={
              "http://localhost:3001/public-dashboards/c40861f4fda2438e8b27c0590fdcb0c6"
            }
            name="Cathode Mixing"
          />
        )}
        {selectedMachine === "Cathode Inspection" && (
          <GrafanaMachineDisplay
            url={
              "http://localhost:3001/public-dashboards/c40861f4fda2438e8b27c0590fdcb0c6"
            }
            name="Cathode Mixing"
          />
        )}
        {selectedMachine === "Anode Mixing" && (
          <GrafanaMachineDisplay
            url={
              "http://localhost:3001/public-dashboards/c40861f4fda2438e8b27c0590fdcb0c6"
            }
            name="Cathode Mixing"
          />
        )}
        {selectedMachine === "Anode Coating" && (
          <GrafanaMachineDisplay
            url={
              "http://localhost:3001/public-dashboards/c40861f4fda2438e8b27c0590fdcb0c6"
            }
            name="Cathode Mixing"
          />
        )}
        {selectedMachine === "Anode Drying" && (
          <GrafanaMachineDisplay
            url={
              "http://localhost:3001/public-dashboards/c40861f4fda2438e8b27c0590fdcb0c6"
            }
            name="Cathode Mixing"
          />
        )}
        {selectedMachine === "Anode Calendaring" && (
          <GrafanaMachineDisplay
            url={
              "http://localhost:3001/public-dashboards/c40861f4fda2438e8b27c0590fdcb0c6"
            }
            name="Cathode Mixing"
          />
        )}
        {selectedMachine === "Anode Slitting" && (
          <GrafanaMachineDisplay
            url={
              "http://localhost:3001/public-dashboards/c40861f4fda2438e8b27c0590fdcb0c6"
            }
            name="Cathode Mixing"
          />
        )}
        {selectedMachine === "Anode Inspection" && (
          <GrafanaMachineDisplay
            url={
              "http://localhost:3001/public-dashboards/c40861f4fda2438e8b27c0590fdcb0c6"
            }
            name="Cathode Mixing"
          />
        )}
        {selectedMachine === "Rewinding" && (
          <GrafanaMachineDisplay
            url={
              "http://localhost:3001/public-dashboards/c40861f4fda2438e8b27c0590fdcb0c6"
            }
            name="Cathode Mixing"
          />
        )}
        {selectedMachine === "Electrolyte Filling" && (
          <GrafanaMachineDisplay
            url={
              "http://localhost:3001/public-dashboards/c40861f4fda2438e8b27c0590fdcb0c6"
            }
            name="Cathode Mixing"
          />
        )}
        {selectedMachine === "Formation Cycling" && (
          <GrafanaMachineDisplay
            url={
              "http://localhost:3001/public-dashboards/c40861f4fda2438e8b27c0590fdcb0c6"
            }
            name="Cathode Mixing"
          />
        )}
        {selectedMachine === "Aging" && (
          <GrafanaMachineDisplay
            url={
              "http://localhost:3001/public-dashboards/c40861f4fda2438e8b27c0590fdcb0c6"
            }
            name="Cathode Mixing"
          />
        )}
      </div>
    </div>
  );
}

export default RealTimeDataPage;
