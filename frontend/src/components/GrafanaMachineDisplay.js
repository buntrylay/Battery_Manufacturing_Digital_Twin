import React from "react";

export function GrafanaMachineDisplay({ name, url }) {
  return (
    <div>
      <div className="data-grid">
        <h3>{name} - Grafana Dashboard Overview</h3>
        <div>
          <iframe
            title="{Name} Grafana Dashboard"
            src={url}
            style={{ width: "100%", height: "800px", border: "none" }}
          ></iframe>
        </div>
      </div>
    </div>
  );
}

export default GrafanaMachineDisplay;
