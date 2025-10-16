import React from "react";
//Component to display Grafana dashboard in an iframe
export function GrafanaMachineDisplay({ name, url }) {
  return (
    <div>
      <div className="data-grid">
        <h3>{name} - Grafana Dashboard Overview</h3>
        <div className="">
          <iframe
            title="{Name} Grafana Dashboard"
            src={url}
            className={"grafana-iframe"}
          ></iframe>
        </div>
      </div>
    </div>
  );
}

export default GrafanaMachineDisplay;
