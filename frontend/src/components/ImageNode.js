// src/components/ImageNode.js
import React from "react";
import { Handle, Position } from "@xyflow/react";

const ImageNode = ({ data }) => {
  console.log(
    "ImageNode data:",
    data.label,
    "status:",
    data.status,
    "simulationStarted:",
    data.simulationStarted
  );

  // Determine border color based on the node's status
  const getBorderColor = (status) => {
    switch (status) {
      case "running":
        return "3px solid #28a745"; // Green
      case "completed":
        return "3px solid #007bff"; // Blue
      case "idle":
        return "3px solid #6c757d"; // Gray - ready for next batch
      case "off":
        return "3px solid #337ec0ff";
      default:
        return "3px solid #dc3545";
    }
  };

  // Determine additional styling for animations
  const getNodeStyle = (status, simulationStarted) => {
    const baseStyle = {
      border: getBorderColor(status),
      borderRadius: "8px",
      padding: "10px",
      backgroundColor: "#fff",
      textAlign: "center",
      width: 150,
      transition: "all 0.3s ease",
    };

    // Machine states and their corresponding styles
    if (status === "running") {
      return {
        ...baseStyle,
        animation: "pulse 2s infinite",
        boxShadow: "0 0 25px rgba(40, 167, 69, 0.8)",
        transform: "scale(1.1)",
        border: "4px solid #28a745",
      };
    }

    if (status === "completed") {
      return {
        ...baseStyle,
        boxShadow: "0 0 15px rgba(0, 123, 255, 0.5)",
        border: "3px solid #007bff",
      };
    }

    if (status === "idle") {
      return {
        ...baseStyle,
        border: "3px solid #6c757d",
        opacity: 0.8,
        transform: "scale(1.0)",
        boxShadow: "0 0 10px rgba(108, 117, 125, 0.3)",
      };
    }

    if (simulationStarted && !status) {
      return {
        ...baseStyle,
        opacity: 0.6,
        transform: "scale(0.95)",
        border: "2px solid #6c757d",
      };
    }

    return baseStyle;
  };

  return (
    <div style={getNodeStyle(data.status, data.simulationStarted)}>
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
