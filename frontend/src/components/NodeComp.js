import React from "react";
import { stageIcons, stageDescriptions } from "./constants";

const NodeComp = ({ m, onClick }) => (
  <div className="flow-node" data-group={m.group} onClick={() => onClick(m.id)}>
    <div className="node-icon">{stageIcons[m.id]}</div>
    <div className="node-label">{m.label}</div>
    <small>Group: {m.group}</small>
    <div className="node-tooltip">{stageDescriptions[m.id]}</div>
  </div>
);

export default NodeComp;
