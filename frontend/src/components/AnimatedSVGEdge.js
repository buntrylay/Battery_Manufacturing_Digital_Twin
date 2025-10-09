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

  // Dynamic animation speed based on simulation status
  const animationDuration = data?.isActive ? "2s" : "4s";
  const particleColor = data?.isActive ? "#28a745" : "#007bff";
  const particleSize = data?.isActive ? "6" : "4";

  return (
    <>
      {/* The base line of the edge */}
      <BaseEdge 
        id={id} 
        path={edgePath} 
        style={{ stroke: data?.isActive ? '#28a745' : '#007bff', strokeWidth: data?.isActive ? 3 : 2 }}
      />
      
      {/* Animated particles */}
      <circle r={particleSize} fill={particleColor}>
        <animateMotion dur={animationDuration} repeatCount="indefinite" path={edgePath} />
      </circle>
      
      {/* Additional particle for active flows */}
      {data?.isActive && (
        <circle r="3" fill="#28a745" opacity="0.6">
          <animateMotion dur="3s" repeatCount="indefinite" path={edgePath} begin="1s" />
        </circle>
      )}
      
      {/* Progress indicator for material flow - Package animation */}
      {data?.showProgress && (
        <>
          <path
            d={edgePath}
            fill="none"
            stroke="#ffc107"
            strokeWidth="4"
            strokeDasharray="8,4"
            opacity="0.7"
          >
            <animate
              attributeName="stroke-dashoffset"
              values="0;-12"
              dur="2s"
              repeatCount="1"
            />
          </path>
          
          {/* Package icon moving along the path */}
          <g>
            <rect x="-6" y="-4" width="12" height="8" fill="#ffc107" stroke="#ff8c00" strokeWidth="1" rx="2">
              <animateMotion dur="2s" repeatCount="1" path={edgePath} />
            </rect>
          </g>
        </>
      )}
    </>
  );
}

export default AnimatedSVGEdge;
