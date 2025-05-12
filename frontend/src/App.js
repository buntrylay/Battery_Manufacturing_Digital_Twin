import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [anode, setAnode] = useState({ PVDF: "", CA: "", AM: "", Solvent: "" });
  const [cathode, setCathode] = useState({ PVDF: "", CA: "", AM: "", Solvent: "" });
  const [status, setStatus] = useState("");

  const handleChange = (type, field, value) => {
    if (type === "Anode") setAnode(prev => ({ ...prev, [field]: value }));
    else setCathode(prev => ({ ...prev, [field]: value }));
  };

  const validateRatios = () => {
    const sum = obj => Object.values(obj).reduce((acc, val) => acc + parseFloat(val || 0), 0);
    const anodeSum = sum(anode);
    const cathodeSum = sum(cathode);

    if (Math.abs(anodeSum - 1) > 0.0001 || Math.abs(cathodeSum - 1) > 0.0001) {
      setStatus("Error: Both Anode and Cathode inputs must total exactly 1.00");
      return false;
    }
    return true;
  };


  const startBothSimulations = async () => {
    if (!validateRatios()) return;

    const data = {
      anode: { ...anode, electrode_type: "Anode" },
      cathode: { ...cathode, electrode_type: "Cathode" }
    };

    try {
      const response = await axios.post("http://localhost:8000/start-both", data);
      setStatus(response.data.message);
    } catch (err) {
      setStatus("Error: " + (err.response?.data?.detail || err.message));
    }
  };

  const resetSimulation = async () => {
    setAnode({ PVDF: "", CA: "", AM: "", Solvent: "" });
    setCathode({ PVDF: "", CA: "", AM: "", Solvent: "" });
    setStatus("Inputs cleared.");
  };

  const downloadZip = (type) => {
    window.open(`http://localhost:8000/files/${type}`, "_blank");
  };

  const downloadAllResults = () => {
    window.open("http://localhost:8000/files/all", "_blank");
  };

  return (
    <div className="container">
      <h2>Battery Slurry Mixing Simulation</h2>

      <div className="simulation-section">
        {["Anode", "Cathode"].map(type => (
          <div key={type} className="input-group">
            <h3>{type} Input</h3>
            {["PVDF", "CA", "AM", "Solvent"].map(field => (
              <input
                key={field}
                type="number"
                placeholder={`${field} ratio`}
                value={type === "Anode" ? anode[field] : cathode[field]}
                onChange={e => handleChange(type, field, e.target.value)}
                step="0.01"
                min="0"
                max="1"
              />
            ))}
          </div>
        ))}
      </div>

      <div className="actions">
        <button onClick={() => downloadZip("Anode")}>Download Anode results</button>
        <button onClick={resetSimulation}>Reset Inputs</button>
        <button onClick={() => downloadZip("Cathode")}>Download Cathode results</button>
        <button onClick={startBothSimulations}>Start Both Simulations</button>
      </div>

      <p className="status-message">{status}</p>
    </div>
  );
}

export default App;
