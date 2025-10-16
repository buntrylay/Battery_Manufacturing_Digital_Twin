import React, { useState, useEffect, useRef } from "react";
import { useFlowPage } from "../contexts/FlowPageContext";
import SidePanel from "../components/SidePanel";
import MachineFlowDiagram from "../components/MachineFlowDiagram";
import "../styles/FlowPage.css";
import { useLogs } from "../contexts/WebSocketContext";
import ToggleSwitch from "../components/ToggleSwitch";
import { startSimulation, getPlantState } from "../services/api";
import { useFactorySimulation } from "../contexts/FactorySimulationContext"; // ✅ Added context import

function FlowPage() {
  const { setSelectedId, selectedStage } = useFlowPage();
  const { clearLogs } = useLogs();
  const [simulationStatus, setSimulationStatus] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [animationTrigger, setAnimationTrigger] = useState(false);
  const [, setPlantState] = useState(null);
  const { setMachineStatusByBatch } = useFactorySimulation();

  const lastSyncTime = useRef(0);

  // Effect to check localStorage on component mount to maintain animation state on refresh
  useEffect(() => {
    if (localStorage.getItem("simulationRunning") === "true") {
      setAnimationTrigger(true);
    }
  }, []);

  const handleClearLogs = () => {
    clearLogs();
    setAnimationTrigger(false);
    localStorage.removeItem("simulationRunning");
  };

  const handleStartFullSimulation = async () => {
    setIsRunning(true);
    setSimulationStatus("Starting full plant simulation...");

    try {
      const response = await startSimulation();

      if (response.data && response.data.message) {
        setSimulationStatus(`✓ ${response.data.message}`);
      } else {
        setSimulationStatus("✓ Plant simulation started successfully!");
      }

      setAnimationTrigger(true);
      localStorage.setItem("simulationRunning", "true");

      handleRefreshPlantState();
    } catch (error) {
      console.error("Simulation start error:", error);
      setSimulationStatus(
        `❌ Error: ${error.response?.data?.detail || error.message}`
      );
    } finally {
      setIsRunning(false);
    }
  };

  const handleRefreshPlantState = async () => {
    try {
      const response = await getPlantState();
      setPlantState(response.data);

      // ✅ Sync global machine state for visual consistency
      if (response.data.machineStates) {
        setMachineStatusByBatch(response.data.machineStates);
      }
    } catch (error) {
      console.error("Plant state error:", error);
    }
  };

  // Auto re-sync backend plant state when returning/focusing Flow Page (3s throttle)
  useEffect(() => {
    const handleFocus = async () => {
      const now = Date.now();
      if (now - lastSyncTime.current < 3000) return; // throttle (3s)
      lastSyncTime.current = now;

      try {
        const res = await getPlantState();
        setPlantState(res.data);

        if (res.data.machineStates) {
          setMachineStatusByBatch(res.data.machineStates);
        }
      } catch (err) {
        console.warn("⚠️ Failed to refresh plant state:", err);
      }
    };

    window.addEventListener("focus", handleFocus);
    handleFocus(); // run immediately on mount

    return () => window.removeEventListener("focus", handleFocus);
  }, [setMachineStatusByBatch]);

  return (
    <div className={`flow-layout ${selectedStage ? "with-panel" : "full"}`}>
      <div className="main-content">
        <h2 className="page-title">
          Lithium-Ion Digital Twin Battery Manufacturing Plant
        </h2>
        <ToggleSwitch
          label="Quick Tips"
          infoContent={
            <div className="instructions">
              <p>1. Click on any machine to configure its parameters.</p>
              <p>2. Use "Load Current" → "Apply Changes" workflow.</p>
              <p>
                3. Click "Add Batch" to add a batch to the continuous plant
                simulation.
              </p>
              <p>4. Use "Reset Plant" to stop all simulations.</p>
            </div>
          }
        />

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

          <div className="status-display">
            {simulationStatus && (
              <p className="simulation-status">{simulationStatus}</p>
            )}
          </div>
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
