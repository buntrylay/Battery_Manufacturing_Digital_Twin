import React, { useState, useEffect } from "react";
import { useFlowPage } from "../contexts/FlowPageContext";
import SidePanel from "../components/SidePanel";
import MachineFlowDiagram from "../components/MachineFlowDiagram";
import "../styles/FlowPage.css";
import { useLogs } from "../contexts/WebSocketContext";
import ToggleSwitch from "../components/ToggleSwitch";
import { startSimulation } from "../services/api";

function FlowPage() {
  const { setSelectedId, selectedStage } = useFlowPage();
  const { clearLogs } = useLogs();
  const [simulationStatus, setSimulationStatus] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [animationTrigger, setAnimationTrigger] = useState(false);
  const [plantState, setPlantState] = useState(null);

  // Effect to check localStorage on component mount to maintain animation state on refresh
  useEffect(() => {
    if (localStorage.getItem("simulationRunning") === "true") {
      setAnimationTrigger(true);
    }
  }, []);

  const handleClearLogs = () => {
    clearLogs();
    setAnimationTrigger(false); // Reset animation when clearing logs
    localStorage.removeItem("simulationRunning"); // Clear persisted state
  };

  const handleStartFullSimulation = async () => {
    setIsRunning(true);
    setAnimationTrigger(true);
    localStorage.setItem("simulationRunning", "true"); // Persist animation state
    setSimulationStatus("Starting full plant simulation...");
    clearLogs();

    try {
      // This API call aligns with adding a batch to a continuous simulation
      const response = await startSimulation();

      if (response.data && response.data.message) {
        setSimulationStatus(`✓ ${response.data.message}`);
      } else {
        setSimulationStatus("✓ Plant simulation started successfully!");
      }

      // Refresh plant state after starting
    } catch (error) {
      console.error("Simulation start error:", error);
      setSimulationStatus(
        `❌ Error: ${error.response?.data?.detail || error.message}`
      );
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className={`flow-layout ${selectedStage ? "with-panel" : "full"}`}>
      <div className="main-content">
        <h2 className="page-title">
          Lithium-Ion Battery Manufacturing Simulation
        </h2>
        <ToggleSwitch
          label="Quick Tips"
          infoContent={
            <div className="instructions">
              <p>1. Click on any machine to configure its parameters.</p>
              <p>
                2. Use "Load Current" → "Validate" → "Apply Changes" workflow.
              </p>
              <p>
                3. Click "Add Batch" to add a batch to the continuous plant
                simulation.
              </p>
              <p>
                4. Use "Refresh State" to check plant status and "Reset Plant"
                to stop all simulations.
              </p>
            </div>
          }
        />
        {/* This container correctly uses the '.controls' class from your CSS */}
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
            {isRunning ? "Adding Batch..." : "Add Batch"}
          </button>
        </div>

        {/* This wrapper for status and plant state matches your CSS structure */}
        <div className="status-messages">
          {simulationStatus && (
            <p className="simulation-status">{simulationStatus}</p>
          )}
          {plantState && (
            <div className="plant-state">
              <strong>Plant Status:</strong>{" "}
              <pre>{JSON.stringify(plantState, null, 2)}</pre>
            </div>
          )}
        </div>

        <div
          className={`flow-canvas ${
            animationTrigger ? "simulation-started" : ""
          }`}
        >
          <MachineFlowDiagram animationTrigger={animationTrigger} />
          {selectedStage && (
            <SidePanel
              selectedStage={selectedStage}
              onClose={() => setSelectedId(null)}
              isOpen={!!selectedStage}
            />
          )}
        </div>
      </div>
    </div>
  );
}

export default FlowPage;
