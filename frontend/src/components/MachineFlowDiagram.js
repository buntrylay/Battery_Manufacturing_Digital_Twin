// src/components/MachineFlowDiagram.js
import React, { useMemo, useEffect, useState, use } from "react";
import {
  ReactFlow,
  useNodesState,
  useEdgesState,
  Background,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

import { useFlowPage } from "../contexts/FlowPageContext";
import { useLogs } from "../contexts/WebSocketContext";
import AnimatedSVGEdge from "./AnimatedSVGEdge";
import ImageNode from "./ImageNode";
import mixingImg from "../assets/mixing.PNG";
import coatingImg from "../assets/coating.PNG";
import dryingImg from "../assets/drying.PNG";
import calendaringImg from "../assets/calendaring.PNG";
import slittingImg from "../assets/slitting.PNG";
import inspectionImg from "../assets/inspection.PNG";
import electrolyteImg from "../assets/electrolyte.PNG";
import rewindingImg from "../assets/rewinding.PNG";
import formationImg from "../assets/formation.PNG";
import agingImg from "../assets/aging.PNG";
const edgeTypes = {
  animated: AnimatedSVGEdge,
};
const nodeTypes = {
  imageNode: ImageNode,
};
const stageImages = {
  "Cathode Mixing": mixingImg,
  "Cathode Coating": coatingImg,
  "Cathode Drying": dryingImg,
  "Cathode Calendaring": calendaringImg,
  "Cathode Slitting": slittingImg,
  "Cathode Inspection": inspectionImg,
  "Anode Mixing": mixingImg,
  "Anode Coating": coatingImg,
  "Anode Drying": dryingImg,
  "Anode Calendaring": calendaringImg,
  "Anode Slitting": slittingImg,
  "Anode Inspection": inspectionImg,
  Rewinding: rewindingImg,
  "Electrolyte Filling": electrolyteImg,
  "Formation Cycling": formationImg,
  Aging: agingImg,
};

// Intial layout generation function
const generateLayout = (machineData) => {
  const nodes = [];
  const edges = [];
  const xSpacing = 220;
  const ySpacing = 180;

  // Function to create a node
  const createNode = (stage, position) => ({
    id: stage.id,
    position,
    type: "imageNode",
    data: {
      label: stage.label,
      imgSrc: stageImages[stage.id],
      status: null,
    },
  });

  // Cathode Line (Top Row)
  const cathodeStages = machineData.slice(0, 6);
  cathodeStages.forEach((stage, i) => {
    nodes.push(createNode(stage, { x: i * xSpacing, y: 0 }));
    if (i > 0) {
      edges.push({
        id: `${cathodeStages[i - 1].id}->${stage.id}`,
        source: cathodeStages[i - 1].id,
        target: stage.id,
      });
    }
  });

  // Anode Line (Middle Row)
  const anodeStages = machineData.slice(6, 12);
  anodeStages.forEach((stage, i) => {
    nodes.push(createNode(stage, { x: i * xSpacing, y: ySpacing }));
    if (i > 0) {
      edges.push({
        id: `${anodeStages[i - 1].id}->${stage.id}`,
        source: anodeStages[i - 1].id,
        target: stage.id,
      });
    }
  });

  // Shared Stages
  const sharedStages = machineData.slice(12);
  sharedStages.forEach((stage, i) => {
    const xPos = (cathodeStages.length - 2 + i) * xSpacing;
    nodes.push(createNode(stage, { x: xPos, y: ySpacing * 2 }));

    if (i > 0) {
      edges.push({
        id: `${sharedStages[i - 1].id}->${stage.id}`,
        source: sharedStages[i - 1].id,
        target: stage.id,
      });
    }
  });

  // Connect the final electrode stages to the first shared stage
  edges.push({
    id: "Cathode Inspection->Rewinding",
    source: "Cathode Inspection",
    target: "Rewinding",
  });
  edges.push({
    id: "Anode Inspection->Rewinding",
    source: "Anode Inspection",
    target: "Rewinding",
  });

  return { defaultNodes: nodes, defaultEdges: edges };
};

const MachineFlowDiagram = () => {
  const { MACHINE_FLOW, setSelectedId } = useFlowPage();
  const { stageLog } = useLogs();
  // Generate default layout only once
  const { defaultNodes, defaultEdges } = useMemo(
    () => generateLayout(MACHINE_FLOW),
    [MACHINE_FLOW]
  );
  //Setting states for Node edge and stage completion
  const [nodes, setNodes, onNodesChange] = useNodesState(defaultNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(defaultEdges);
  const [machineStatus, setMachineStatus] = useState({});
  useEffect(() => {
    setNodes((nds) =>
      nds.map((node) => ({
        ...node,
        data: { ...node.data, status: machineStatus[node.id] || null },
      }))
    );
  }, [machineStatus, setNodes]);

  // TODO: This listens for WebSocket logs and updates state
  useEffect(() => {
    if (stageLog.length === 0) {
      setMachineStatus({});
      return;
    }
    const latestLog = stageLog[stageLog.length - 1];
    const [stageId, status] = latestLog.split(":");

    if (status && status.trim() === "complete") {
      const completedStageId = stageId.trim();

      // Find the index of the machine that just finished
      const completedIndex = MACHINE_FLOW.findIndex(
        (m) => m.id === completedStageId
      );

      let nextStageId = null;
      // If it's not the last machine, find the next one
      if (completedIndex > -1 && completedIndex < MACHINE_FLOW.length - 1) {
        nextStageId = MACHINE_FLOW[completedIndex + 1].id;
      }

      // Update the status for both the completed and the next running machine
      setMachineStatus((prevStatus) => {
        const newStatus = { ...prevStatus, [completedStageId]: "completed" };
        if (nextStageId) {
          newStatus[nextStageId] = "running";
        }
        return newStatus;
      });
    }
  }, [stageLog, MACHINE_FLOW]);

  //TODO: Update the edge based of the machine status from Websocket
  useEffect(() => {
    setEdges((eds) =>
      eds.map((edge) => {
        const sourceStatus = machineStatus[edge.source];
        const targetStatus = machineStatus[edge.target];

        if (sourceStatus === "completed" && targetStatus === "running") {
          return { ...edge, type: "animated", animated: true };
        } else {
          return { ...edge, type: "default", animated: true };
        }
      })
    );
  }, [machineStatus, setEdges]);

  const onNodeClick = (_, node) => setSelectedId(node.id);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeClick={onNodeClick}
      edgeTypes={edgeTypes}
      fitView
      nodeTypes={nodeTypes}
    >
      <Background />
    </ReactFlow>
  );
};

export default MachineFlowDiagram;
