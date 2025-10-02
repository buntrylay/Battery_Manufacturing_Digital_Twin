import React from "react";

export function GrafanaMachineDisplay({ name, url }) {
  return (
    <div>
      <h3>{name} Data Visualization</h3>
      <div className="data-grid">
        <div className="data-card">
          <h3>Machine Status</h3>
          <div>
            <iframe
              title="{Name} Grafana Dashboard"
              src={url}
              style={{ width: "100%", height: "600px", border: "none" }}
            ></iframe>
          </div>
        </div>

        <div className="data-card">
          <h3>Current Batch</h3>
          <div className="placeholder"></div>
        </div>

        <div className="data-card">
          <h3>Sensor Information</h3>
          <div className="placeholder"></div>
        </div>

        <div className="data-card">
          <h3>Sensor Information</h3>
          <div className="placeholder"></div>
        </div>
      </div>
    </div>
  );
}

export default GrafanaMachineDisplay;
