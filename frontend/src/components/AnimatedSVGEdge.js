// src/components/AnimatedSVGEdge.js
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
}) {
  const [edgePath] = getSmoothStepPath({
    sourceX,
    sourceY,
    sourcePosition,
    targetX,
    targetY,
    targetPosition,
  });

  return (
    <>
      {/* The base line of the edge */}
      <BaseEdge id={id} path={edgePath} />

      <circle r="4" fill="#007bff">
        <animateMotion
          dur="1s"
          repeatCount="indefinite"
          path={edgePath}
          fill="freeze"
        />
      </circle>
    </>
  );
}

export default AnimatedSVGEdge;
