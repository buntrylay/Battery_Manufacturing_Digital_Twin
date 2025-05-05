import React, { useState, useEffect, useRef } from "react";
import "./App.css";

function App() {
  const [cathodeInputs, setCathodeInputs] = useState({ NMP: "", PVDF: "", CB: "", LMNC: "" });
  const [anodeInputs, setAnodeInputs] = useState({ Water: "", PVDF: "", CB: "", Graphite: "" });
  const [batteries, setBatteries] = useState("");
  const [time, setTime] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [stage, setStage] = useState("");
  const intervalRef = useRef(null);

  const handleInputChange = (setter, key) => (e) => {
    let value = e.target.value;
    if (/^\d{0,3}(\.\d{0,2})?$/.test(value) && Number(value) <= 100) {
      setter((prev) => ({ ...prev, [key]: value }));
    }
  };

  const sumPercentages = (inputs) => {
    return Object.values(inputs).reduce((sum, val) => sum + Number(val || 0), 0);
  };

  useEffect(() => {
    if (isRunning) {
      intervalRef.current = setInterval(() => {
        setTime((prev) => prev + 1);
      }, 1000);
    } else {
      clearInterval(intervalRef.current);
    }
    return () => clearInterval(intervalRef.current);
  }, [isRunning]);

  useEffect(() => {
    if (time < 20) setStage("Binder + Solvent");
    else if (time < 40) setStage("Add Active Material");
    else if (time < 60) setStage("Final Mixing");
    else setStage("Complete");
  }, [time]);

  const formatTime = (seconds) => {
    const h = String(Math.floor(seconds / 3600)).padStart(2, '0');
    const m = String(Math.floor((seconds % 3600) / 60)).padStart(2, '0');
    const s = String(seconds % 60).padStart(2, '0');
    return `${h}:${m}:${s}`;
  };

  const handleStart = () => setIsRunning(true);
  const handlePause = () => setIsRunning(false);
  const handleReset = () => {
    setIsRunning(false);
    setTime(0);
    setStage("");
  };

  const cathodeTotal = sumPercentages(cathodeInputs);
  const anodeTotal = sumPercentages(anodeInputs);

  return (
    <div className="container">
      <div className="battery-input">
        <label className="label">Batteries:</label>
        <input
          type="text"
          value={batteries}
          onChange={(e) => setBatteries(e.target.value)}
          className="input"
        />
      </div>

      <div className="section-row">
        {/* Cathode Section */}
        <div className="section">
          <h2 className="section-title">Cathode</h2>
          <div className="input-group red-bg">
            <p className="sub-label">Inputs:</p>
            {Object.keys(cathodeInputs).map((item) => (
              <input
                key={item}
                placeholder={`${item} (%)`}
                value={cathodeInputs[item]}
                onChange={handleInputChange(setCathodeInputs, item)}
                className="input-box"
              />
            ))}
            <p className="warning">Total: {cathodeTotal}% {cathodeTotal > 100 && "(Over 100%!)"}</p>
          </div>

          <div className="output-box">
            <p className="sub-label">Live Outputs:</p>
            {["Density", "Viscosity", "Yield Stress"].map((label) => (
              <div key={label} className="output-row">
                <span>{label}</span>
                <span>Auto</span>
              </div>
            ))}
          </div>

          <div className="output-box">
            <p className="sub-label">Factors:</p>
            {["Temperature", "RPM", "Pressure"].map((label) => (
              <div key={label} className="output-row">
                <span>{label}</span>
                <span>Auto</span>
              </div>
            ))}
          </div>

          <div className="meta">
            <label className="bold-label">Time:</label>
            <input className="input" value={formatTime(time)} readOnly />
          </div>
          <div className="meta">
            <label className="bold-label">Current Stage:</label>
            <input className="input" value={stage} readOnly />
          </div>
        </div>

        {/* Anode Section */}
        <div className="section">
          <h2 className="section-title">Anode</h2>
          <div className="input-group blue-bg">
            <p className="sub-label">Inputs:</p>
            {Object.keys(anodeInputs).map((item) => (
              <input
                key={item}
                placeholder={`${item} (%)`}
                value={anodeInputs[item]}
                onChange={handleInputChange(setAnodeInputs, item)}
                className="input-box"
              />
            ))}
            <p className="warning">Total: {anodeTotal}% {anodeTotal > 100 && "(Over 100%!)"}</p>
          </div>

          <div className="output-box">
            <p className="sub-label">Live Outputs:</p>
            {["Density", "Viscosity", "Yield Stress"].map((label) => (
              <div key={label} className="output-row">
                <span>{label}</span>
                <span>Auto</span>
              </div>
            ))}
          </div>

          <div className="output-box">
            <p className="sub-label">Factors:</p>
            {["Temperature", "RPM", "Pressure"].map((label) => (
              <div key={label} className="output-row">
                <span>{label}</span>
                <span>Auto</span>
              </div>
            ))}
          </div>

          <div className="meta">
            <label className="bold-label">Time:</label>
            <input className="input" value={formatTime(time)} readOnly />
          </div>
          <div className="meta">
            <label className="bold-label">Current Stage:</label>
            <input className="input" value={stage} readOnly />
          </div>
        </div>
      </div>

      <div className="button-row">
        <button className="button pause" onClick={handlePause}>Pause</button>
        <button className="button start" onClick={handleStart}>Start</button>
        <button className="button reset" onClick={handleReset}>Reset</button>
      </div>
    </div>
  );
}

export default App;
