import React, { useState } from "react";
import { useFlowPage } from "../contexts/FlowPageContext";
import SidePanel from "../components/SidePanel";
import MachineFlowDiagram from "../components/MachineFlowDiagram";
import "../styles/FlowPage.css";
import { useLogs } from "../contexts/WebSocketContext";
import { startMixingSimulation } from "../services/api";

const FlowPage = () => {
  const { setSelectedId, selectedStage } = useFlowPage();
  const { clearLogs } = useLogs();
  const [simulationStatus, setSimulationStatus] = useState("");
  const [isRunning, setIsRunning] = useState(false);

  const handleClearLogs = () => {
    clearLogs();
  };

  const handleStartFullSimulation = async () => {
    setIsRunning(true);
    setSimulationStatus("Starting full simulation...");
    clearLogs();

    try {
      // Get saved inputs from localStorage
      const anodeInputs = localStorage.getItem('mixingInputs_Anode Mixing');
      const cathodeInputs = localStorage.getItem('mixingInputs_Cathode Mixing');

      if (!anodeInputs || !cathodeInputs) {
        setSimulationStatus("Error: Please configure both Anode and Cathode mixing inputs first");
        setIsRunning(false);
        return;
      }

      const anodeData = JSON.parse(anodeInputs);
      const cathodeData = JSON.parse(cathodeInputs);

      // Start anode mixing simulation
      setSimulationStatus("Starting Anode mixing simulation...");
      await startMixingSimulation(anodeData);
      
      // Wait a moment between simulations
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Start cathode mixing simulation
      setSimulationStatus("Starting Cathode mixing simulation...");
      await startMixingSimulation(cathodeData);

      setSimulationStatus("Full simulation completed successfully!");
    } catch (error) {
      setSimulationStatus("Error: " + (error.response?.data?.detail || error.message));
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className={`flow-layout ${selectedStage ? "with-panel" : "full"}`}>
      <div className="main-content">
        <div className="controls">
          <button onClick={handleClearLogs} className="clear-logs-button">
            Clear Logs
          </button>
          <button 
            onClick={handleStartFullSimulation} 
            className="start-full-simulation-btn"
            disabled={isRunning}
          >
            {isRunning ? "Running..." : "Start Full Simulation"}
          </button>
          <div className="instructions">
            <p>1. Configure mixing inputs by clicking on Anode/Cathode Mixing machines</p>
            <p>2. Save inputs in each machine's side panel</p>
            <p>3. Click "Start Full Simulation" to run the complete process</p>
            {simulationStatus && <p className="simulation-status">{simulationStatus}</p>}
          </div>
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
