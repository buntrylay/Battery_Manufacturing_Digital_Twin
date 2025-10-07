import React, { useState } from "react";
import { useFlowPage } from "../contexts/FlowPageContext";
import SidePanel from "../components/SidePanel";
import MachineFlowDiagram from "../components/MachineFlowDiagram";
import "../styles/FlowPage.css";
import { useLogs } from "../contexts/WebSocketContext";
import { startSimulation } from "../services/api";
import ToggleSwitch from "../components/ToggleSwitch";
const FlowPage = () => {
  const { setSelectedId, selectedStage } = useFlowPage();
  const { clearLogs, addLog } = useLogs();
  const [simulationStatus, setSimulationStatus] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [animationTrigger, setAnimationTrigger] = useState(false);

  const handleClearLogs = () => {
    clearLogs();
    setAnimationTrigger(false); // Reset animation when clearing logs
  };

  const handleStartFullSimulation = async () => {
    setIsRunning(true);
    setAnimationTrigger(true);
    setSimulationStatus("Starting full simulation...");
    clearLogs();

    try {
      // Get saved inputs from localStorage
      const anodeInputs = localStorage.getItem("mixingInputs_Anode Mixing");
      const cathodeInputs = localStorage.getItem("mixingInputs_Cathode Mixing");

      if (!anodeInputs || !cathodeInputs) {
        setSimulationStatus(
          "Error: Please configure both Anode and Cathode mixing inputs first"
        );
        setIsRunning(false);
        return;
      }

      const anodeData = JSON.parse(anodeInputs);
      const cathodeData = JSON.parse(cathodeInputs);

      // Prepare simulation data with both anode and cathode parameters
      const simulationData = {
        anode_params: {
          AM: anodeData.AM,
          CA: anodeData.CA,
          PVDF: anodeData.PVDF,
          Solvent: anodeData.Solvent,
        },
        cathode_params: {
          AM: cathodeData.AM,
          CA: cathodeData.CA,
          PVDF: cathodeData.PVDF,
          Solvent: cathodeData.Solvent,
        },
      };

      setSimulationStatus(
        "Starting complete battery manufacturing simulation..."
      );
      const response = await startSimulation(simulationData);

      setSimulationStatus(
        `Full simulation started successfully! Batch ID: ${response.data.batch_id}`
      );
    } catch (error) {
      setSimulationStatus(
        "Error: " + (error.response?.data?.detail || error.message)
      );
    } finally {
      setIsRunning(false);
      // Keep animation trigger active to show ongoing simulation
    }
  };

  return (
    <div className={`flow-layout ${selectedStage ? "with-panel" : "full"}`}>
      <div className="main-content">
        <ToggleSwitch
          label="Quick Tips"
          infoContent={
            <div className="instructions">
              <p>Instructions:</p>
              <p>1. Configure inputs by clicking on Machines.</p>
              <p>2. Save inputs in each machine's side panel.</p>
              <p>
                3. Click "Start Full Simulation" to run the complete battery
                manufacturing process.
              </p>
            </div>
          }
        />

        <h2 className="page-title">Battery Manufacturing Flow</h2>
        <div className="controls">
          <button onClick={handleClearLogs} className="clear-logs-button">
            Clear Logs
          </button>
          <button
            onClick={handleStartFullSimulation}
            className={`start-full-simulation-btn ${
              isRunning ? "running" : ""
            }`}
            disabled={isRunning}
          >
            {isRunning ? "Running..." : "Start Full Simulation"}
          </button>
        </div>
        <div className="instructions">
          {simulationStatus && (
            <ToggleSwitch
              label="Simulation Status"
              infoContent={
                <div className="instructions">
                  {simulationStatus && (
                    <p className="simulation-status">{simulationStatus}</p>
                  )}
                  {animationTrigger && (
                    <p style={{ color: "green", fontWeight: "bold" }}>
                      Animation Active - Machines are pulsing!
                    </p>
                  )}
                </div>
              }
            />
          )}
        </div>
        <div
          className={`flow-canvas ${
            animationTrigger ? "simulation-started" : ""
          }`}
        >
          <MachineFlowDiagram animationTrigger={animationTrigger} />
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
