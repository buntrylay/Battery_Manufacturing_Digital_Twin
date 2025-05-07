// App.js
import React, { useState } from "react";
import axios from "axios";
import "./App.css"; // <-- Import the CSS file

function App() {
  const [anode, setAnode] = useState({ PVDF: "", CA: "", AM: "", Solvent: "" });
  const [cathode, setCathode] = useState({ PVDF: "", CA: "", AM: "", Solvent: "" });
  const [status, setStatus] = useState("");

  const handleChange = (type, field, value) => {
    if (type === "Anode") setAnode(prev => ({ ...prev, [field]: value }));
    else setCathode(prev => ({ ...prev, [field]: value }));
  };

  const startSimulation = async (type) => {
    const data = type === "Anode"
      ? { ...anode, electrode_type: "Anode" }
      : { ...cathode, electrode_type: "Cathode" };

    try {
      const response = await axios.post("http://localhost:8000/start", data);
      setStatus(response.data.message);
    } catch (err) {
      setStatus("Error: " + (err.response?.data?.detail || err.message));
    }
  };

  const resetSimulation = async () => {
    try {
      const response = await axios.post("http://localhost:8000/reset");
      setStatus(response.data.message);
    } catch (err) {
      setStatus("Error: " + (err.response?.data?.detail || err.message));
    }
  };

  const downloadJson = () => {
    window.open("http://localhost:8000/files", "_blank");
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
            <button onClick={() => startSimulation(type)}>Start {type}</button>
          </div>
        ))}
      </div>

      <div className="actions">
        <button onClick={resetSimulation}>Reset & Delete JSON</button>
        <button onClick={downloadJson}>Download Results</button>
      </div>

      <p className="status-message">{status}</p>
    </div>
  );
}

export default App;
