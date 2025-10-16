import React from "react";
import { BaseEdge, getSmoothStepPath } from "@xyflow/react";

export function AnimatedSVGEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  data,
}) {
  const [edgePath] = getSmoothStepPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  const isActive = data?.isActive;
  const showProgress = data?.showProgress;

  return (
    <>
      {/* 🖤 Always-visible base connection (thin black line) */}
      <BaseEdge
        id={`${id}-base`}
        path={edgePath}
        style={{
          stroke: "#222",
          strokeWidth: 1.5,
          opacity: 0.4,
        }}
      />

      {/* When machine is active Animation Overlay */}
      {isActive && (
        <>
          <BaseEdge
            id={id}
            path={edgePath}
            style={{
              stroke: "#28a745",
              strokeWidth: 3,
              opacity: 0.9,
            }}
          />
          <circle r="6" fill="#28a745">
            <animateMotion
              dur="1.5s"
              repeatCount="indefinite"
              path={edgePath}
            />
          </circle>
          <circle r="3" fill="#28a745" opacity="0.6">
            <animateMotion
              dur="1.5s"
              repeatCount="indefinite"
              path={edgePath}
              begin="0.3s"
            />
          </circle>
        </>
      )}

      {/*  Represents the package transition between Nodes */}
      {showProgress && (
        <>
          <path
            d={edgePath}
            fill="none"
            stroke="#ffc107"
            strokeWidth="4"
            strokeDasharray="8,4"
            opacity="0.9"
          >
            <animate
              attributeName="stroke-dashoffset"
              values="0;-12"
              dur="2s"
              repeatCount="1"
            />
          </path>
          <circle r="5" fill="#ffcc00">
            <animateMotion dur="2s" repeatCount="1" path={edgePath} />
          </circle>
        </>
      )}
    </>
  );
}

export default AnimatedSVGEdge;
