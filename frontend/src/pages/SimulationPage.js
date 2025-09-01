// pages/SimulationPage.js
import React, { useState, useContext } from "react";
import SlurryInputs from "../components/SlurryInputs";
import { startSimulation, downloadFile } from "../services/api";
import { WebSocketContext } from "../contexts/WebSocketContext";

export default function SimulationPage() {
  const [anode, setAnode] = useState({ PVDF: "", CA: "", AM: "", Solvent: "" });
  const [cathode, setCathode] = useState({
    PVDF: "",
    CA: "",
    AM: "",
    Solvent: "",
  });
  const [status, setStatus] = useState("");
  const { stageLog } = useContext(WebSocketContext);

  const handleChange = (type, field, value) => {
    if (type === "Anode") setAnode((prev) => ({ ...prev, [field]: value }));
    else setCathode((prev) => ({ ...prev, [field]: value }));
  };

  const validateRatios = () => {
    const sum = (obj) =>
      Object.values(obj).reduce((acc, val) => acc + parseFloat(val || 0), 0);
    return (
      Math.abs(sum(anode) - 1) <= 0.0001 && Math.abs(sum(cathode) - 1) <= 0.0001
    );
  };

  const startBothSimulations = async () => {
    if (!validateRatios()) {
      setStatus("Error: Both Anode and Cathode inputs must total exactly 1.00");
      return;
    }
    try {
      const response = await startSimulation({
        anode: { ...anode, electrode_type: "Anode" },
        cathode: { ...cathode, electrode_type: "Cathode" },
      });
      setStatus(response.data.message);
    } catch (err) {
      setStatus("Error: " + (err.response?.data?.detail || err.message));
    }
  };

  const resetSimulation = () => {
    setAnode({ PVDF: "", CA: "", AM: "", Solvent: "" });
    setCathode({ PVDF: "", CA: "", AM: "", Solvent: "" });
    setStatus("Inputs cleared.");
  };

  return (
    <div className="container">
      <h2>Battery Slurry Mixing Simulation</h2>
      <div className="simulation-section">
        <SlurryInputs type="Anode" data={anode} onChange={handleChange} />
        <SlurryInputs type="Cathode" data={cathode} onChange={handleChange} />
      </div>
      <div className="actions">
        <button onClick={() => downloadFile("Anode")}>
          Download Anode results
        </button>
        <button onClick={resetSimulation}>Reset Inputs</button>
        <button onClick={() => downloadFile("Cathode")}>
          Download Cathode results
        </button>
        <button onClick={startBothSimulations}>Start Both Simulations</button>
      </div>
      <p className="status-message">{status}</p>
      <div className="stage-log">
        <h4>Live Stage Updates:</h4>
        <ul>
          {stageLog.map((msg, idx) => (
            <li key={idx}>{msg}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}
