import React from "react";
import { useFlowPage } from "../contexts/FlowPageContext";
import SidePanel from "../components/SidePanel";
import MachineFlowDiagram from "../components/MachineFlowDiagram";
import "../styles/FlowPage.css";
import { useLogs } from "../contexts/WebSocketContext";

const FlowPage = () => {
  const { MACHINE_FLOW, setSelectedId, selectedStage } = useFlowPage();
  const { addLog, clearLogs } = useLogs();

  const sleep = (ms) => new Promise((res) => setTimeout(res, ms));

  const handleStartSimulation = async () => {
    clearLogs();
    await sleep(100);

    // This special log message starts the first machine by marking a "dummy" predecessor as complete.
    if (MACHINE_FLOW.length > 0) {
      addLog(`Start:complete`);
      await sleep(2000);
    }

    // Loop through the rest of the machines
    for (const stage of MACHINE_FLOW) {
      const logMessage = `${stage.id}:complete`;
      console.log(`Simulating: ${logMessage}`);
      addLog(logMessage);
      await sleep(2000);
    }

    console.log("Simulation finished!");
  };

  return (
    <div className={`flow-layout ${selectedStage ? "with-panel" : "full"}`}>
      <div className="main-content">
        <div className="controls">
          <button onClick={handleStartSimulation} className="sim-button">
            Start Dummy Simulation
          </button>
        </div>
        <div className="flow-canvas">
          <MachineFlowDiagram />
        </div>
      </div>

      {selectedStage && (
        <SidePanel
          selectedStage={selectedStage}
          onClose={() => setSelectedId(null)}
        />
      )}
    </div>
  );
};

export default FlowPage;
