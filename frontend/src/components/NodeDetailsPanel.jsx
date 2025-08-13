// src/components/NodeDetailsPanel.js
import React from "react";

export default function NodeDetailsPanel({ node, onClose }) {
  if (!node) {
    return (
      <div style={{ width: 300, background: "#f7f7f7", padding: 20 }}>
        <h3>Stage Details</h3>
        <p>Select a node to view details.</p>
      </div>
    );
  }

  return (
    <div
      style={{
        width: 300,
        background: "#fff",
        padding: 20,
        borderLeft: "1px solid #ccc",
      }}
    >
      <button onClick={onClose} style={{ float: "right" }}>
        X
      </button>
      <h3>{node.data.label}</h3>
      <p>
        <strong>ID:</strong> {node.id}
      </p>
      <p>
        <strong>Position:</strong> x: {node.position.x}, y: {node.position.y}
      </p>
      <p>
        <strong>Status:</strong>{" "}
        {node.style.background === "#90ee90" ? "Active" : "Idle"}
      </p>

      {/* Example of editable parameters */}
      <div>
        <label>Target Time (s):</label>
        <input type="number" defaultValue={10} />
      </div>
      <div>
        <label>Temperature (°C):</label>
        <input type="number" defaultValue={25} />
      </div>
      <button style={{ marginTop: 10 }}>Save</button>
    </div>
  );
}
