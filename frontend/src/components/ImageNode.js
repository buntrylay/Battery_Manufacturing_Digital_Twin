// src/components/ImageNode.js
import React from "react";
import { Handle, Position } from "@xyflow/react";

const ImageNode = ({ data }) => {
  // Determine border color based on the node's status
  const getBorderColor = (status) => {
    switch (status) {
      case "running":
        return "3px solid #28a745"; // Green
      case "off":
        return "3px solid #337ec0ff";
      default:
        return "3px solid #dc3545";
    }
  };

  return (
    // The main style is now dynamic based on data.status
    <div
      style={{
        border: getBorderColor(data.status), // Dynamic border
        borderRadius: "8px",
        padding: "10px",
        backgroundColor: "#fff",
        textAlign: "center",
        width: 150,
        transition: "border 0.3s ease", // Smooth transition for color changes
      }}
    >
      <Handle type="target" position={Position.Left} />

      <img
        src={data.imgSrc}
        alt={data.label}
        style={{ width: "100px", height: "auto", marginBottom: "5px" }}
      />
      <p style={{ margin: 0, fontSize: "14px" }}>{data.label}</p>

      <Handle type="source" position={Position.Right} />
    </div>
  );
};

export default ImageNode;
