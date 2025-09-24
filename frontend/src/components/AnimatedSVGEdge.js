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
      {/* TODO: Add in animation time updates once flow been updated*/}
      <circle r="4" fill="#007bff">
        <animateMotion dur="4s" repeatCount="indefinite" path={edgePath} />
      </circle>
    </>
  );
}

export default AnimatedSVGEdge;
