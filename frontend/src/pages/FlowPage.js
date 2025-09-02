import React from "react";
import { useFlowPage } from "../contexts/FlowPageContext";
import Node from "../components/NodeComp";
import SidePanel from "../components/SidePanel";
import "../styles/FlowPage.css";
const FlowPage = () => {
  const flowPageData = useFlowPage();

  if (!flowPageData || !flowPageData.MACHINE_FLOW) {
    return <div>Loading...</div>;
  }

  const { MACHINE_FLOW, setSelectedId, selectedStage } = flowPageData;

  return (
    <div className="flow-layout">
      <div className="flow-canvas">
        <svg className="connectors" width="100%" height="100%">
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="7"
              refX="10"
              refY="3.5"
              orient="auto"
            >
              <polygon points="0 0, 10 3.5, 0 7" fill="#9ca3af" />
            </marker>
          </defs>
          {/* row 1 arrows */}
          <line x1="10%" y1="25%" x2="30%" y2="25%" className="connector" />
          <line x1="30%" y1="25%" x2="50%" y2="25%" className="connector" />
          <line x1="50%" y1="25%" x2="70%" y2="25%" className="connector" />
          <line x1="70%" y1="25%" x2="90%" y2="25%" className="connector" />
          {/* down at end */}
          <line x1="90%" y1="25%" x2="90%" y2="75%" className="connector" />
          {/* row 2 arrows (right → left) */}
          <line x1="90%" y1="75%" x2="70%" y2="75%" className="connector" />
          <line x1="70%" y1="75%" x2="50%" y2="75%" className="connector" />
          <line x1="50%" y1="75%" x2="30%" y2="75%" className="connector" />
          <line x1="30%" y1="75%" x2="10%" y2="75%" className="connector" />
        </svg>

        {MACHINE_FLOW.map((m) => (
          <Node key={m.id} m={m} onClick={setSelectedId} />
        ))}
      </div>
      <SidePanel selectedStage={selectedStage} />
    </div>
  );
};

export default FlowPage;
