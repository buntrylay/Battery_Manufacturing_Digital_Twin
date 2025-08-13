import React, {
  useContext,
  useMemo,
  useEffect,
  useState,
  useCallback,
} from "react";
import ReactFlow, {
  Background,
  Controls,
  useNodesState,
  useEdgesState,
} from "reactflow";
import "reactflow/dist/style.css";
import { WebSocketContext } from "../contexts/WebSocketContext";
import NodeDetailsPanel from "../components/NodeDetailsPanel";

export default function FlowPage() {
  const { stageLog } = useContext(WebSocketContext);
  const [activeStage, setActiveStage] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);

  const initialNodes = useMemo(
    () => [
      {
        id: "1",
        position: { x: 100, y: 50 },
        data: { label: "Anode Mixing" },
        style: { background: "#eee" },
      },
      {
        id: "2",
        position: { x: 350, y: 50 },
        data: { label: "Cathode Mixing" },
        style: { background: "#eee" },
      },
      {
        id: "3",
        position: { x: 600, y: 50 },
        data: { label: "Electrode Filling" },
        style: { background: "#eee" },
      },
      {
        id: "4",
        position: { x: 850, y: 50 },
        data: { label: "Drying" },
        style: { background: "#eee" },
      },
    ],
    []
  );

  const initialEdges = useMemo(
    () => [
      { id: "e1-3", source: "1", target: "3", animated: true },
      { id: "e2-3", source: "2", target: "3", animated: true },
      { id: "e3-4", source: "3", target: "4", animated: true },
    ],
    []
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Highlight node based on WebSocket messages
  useEffect(() => {
    if (stageLog.length > 0) {
      const latestMessage = stageLog[stageLog.length - 1];
      setActiveStage(latestMessage);

      setNodes((nds) =>
        nds.map((node) => ({
          ...node,
          style: {
            ...node.style,
            background: latestMessage.includes(node.data.label)
              ? "#90ee90"
              : "#eee",
            border: latestMessage.includes(node.data.label)
              ? "2px solid green"
              : "1px solid #ccc",
          },
        }))
      );
    }
  }, [stageLog, setNodes]);

  // Handle node click
  const onNodeClick = useCallback((_, node) => {
    setSelectedNode(node);
  }, []);

  return (
    <div style={{ display: "flex", height: "90vh" }}>
      <div style={{ flex: 1 }}>
        <h2 style={{ textAlign: "center" }}>Simulation Flow</h2>
        {activeStage && (
          <p style={{ textAlign: "center" }}>Current stage: {activeStage}</p>
        )}
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onNodeClick={onNodeClick}
          fitView
        >
          <Background />
          <Controls />
        </ReactFlow>
      </div>

      {/* Node Details Side Panel */}
      <NodeDetailsPanel
        node={selectedNode}
        onClose={() => setSelectedNode(null)}
      />
    </div>
  );
}
