import React from "react";

export function GrafanaWindowDisplay({name, url, width, height}) {
  

  return (
    <div>
        <h3>{name} Data Visualization</h3>     
        <div className="data-grid">
        <div className="data-card">
          <h3>Machine Status</h3>
           <div>
                <iframe
                title="Real-Time Data Visualization"
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
