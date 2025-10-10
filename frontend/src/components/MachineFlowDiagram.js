// src/components/MachineFlowDiagram.js
import React, { useMemo, useEffect, useState, useCallback } from "react";
import {
  ReactFlow,
  useNodesState,
  useEdgesState,
  Background,
  MiniMap,
  Controls,
} from "@xyflow/react";

import { useFactorySimulation } from "../contexts/FactorySimulationContext";

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

/* -------------------------- Types & Registrations -------------------------- */

const edgeTypes = { animated: AnimatedSVGEdge };
const nodeTypes = { imageNode: ImageNode };

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

/* ------------------------------ Layout Builder ----------------------------- */

const generateLayout = (machineData) => {
  const nodes = [];
  const edges = [];
  const xSpacing = 220;
  const ySpacing = 180;

  const createNode = (stage, position) => ({
    id: stage.id,
    position,
    type: "imageNode",
    data: { label: stage.label, imgSrc: stageImages[stage.id], status: null },
  });

  // Cathode (top row)
  const cathodeStages = machineData.slice(0, 6);
  cathodeStages.forEach((stage, i) => {
    nodes.push(createNode(stage, { x: i * xSpacing, y: 0 }));
    if (i > 0) {
      edges.push({
        id: `${cathodeStages[i - 1].id}->${stage.id}`,
        source: cathodeStages[i - 1].id,
        target: stage.id,
        type: "animated",
      });
    }
  });

  // Anode (middle row)
  const anodeStages = machineData.slice(6, 12);
  anodeStages.forEach((stage, i) => {
    nodes.push(createNode(stage, { x: i * xSpacing, y: ySpacing }));
    if (i > 0) {
      edges.push({
        id: `${anodeStages[i - 1].id}->${stage.id}`,
        source: anodeStages[i - 1].id,
        target: stage.id,
        type: "animated",
      });
    }
  });

  // Shared (bottom row)
  const sharedStages = machineData.slice(12);
  sharedStages.forEach((stage, i) => {
    const xPos = (cathodeStages.length - 2 + i) * xSpacing;
    nodes.push(createNode(stage, { x: xPos, y: ySpacing * 2 }));
    if (i > 0) {
      edges.push({
        id: `${sharedStages[i - 1].id}->${stage.id}`,
        source: sharedStages[i - 1].id,
        target: stage.id,
        type: "animated",
      });
    }
  });

  edges.push({
    id: "Cathode Inspection->Rewinding",
    source: "Cathode Inspection",
    target: "Rewinding",
    type: "animated",
  });
  edges.push({
    id: "Anode Inspection->Rewinding",
    source: "Anode Inspection",
    target: "Rewinding",
    type: "animated",
  });

  return { defaultNodes: nodes, defaultEdges: edges };
};

/* ------------------------- Stage Progression Arrays ------------------------ */

const ANODE_FLOW = [
  "Anode Mixing",
  "Anode Coating",
  "Anode Drying",
  "Anode Calendaring",
  "Anode Slitting",
  "Anode Inspection",
];

const CATHODE_FLOW = [
  "Cathode Mixing",
  "Cathode Coating",
  "Cathode Drying",
  "Cathode Calendaring",
  "Cathode Slitting",
  "Cathode Inspection",
];

const SHARED_FLOW = [
  "Rewinding",
  "Electrolyte Filling",
  "Formation Cycling",
  "Aging",
];

const nextOf = (flow, current) => {
  const i = flow.indexOf(current);
  return i >= 0 && i < flow.length - 1 ? flow[i + 1] : null;
};

const whichFlow = (machine) => {
  if (machine.startsWith("Anode")) return ANODE_FLOW;
  if (machine.startsWith("Cathode")) return CATHODE_FLOW;
  return SHARED_FLOW;
};

const isInspection = (m) =>
  m === "Anode Inspection" || m === "Cathode Inspection";

/* ------------------------------ Component ---------------------------------- */

const MachineFlowDiagram = ({ animationTrigger }) => {
  const { MACHINE_FLOW, setSelectedId } = useFlowPage();
  const { stageLog } = useLogs();

  const processToMachineMap = useMemo(
    () => ({
      mixing_anode: "Anode Mixing",
      mixing_cathode: "Cathode Mixing",
      coating_anode: "Anode Coating",
      coating_cathode: "Cathode Coating",
      drying_anode: "Anode Drying",
      drying_cathode: "Cathode Drying",
      calendaring_anode: "Anode Calendaring",
      calendaring_cathode: "Cathode Calendaring",
      slitting_anode: "Anode Slitting",
      slitting_cathode: "Cathode Slitting",
      inspection_anode: "Anode Inspection",
      inspection_cathode: "Cathode Inspection",
      rewinding_cell: "Rewinding",
      electrolyte_filling_cell: "Electrolyte Filling",
      formation_cycling_cell: "Formation Cycling",
      aging_cell: "Aging",
    }),
    []
  );

  const { defaultNodes, defaultEdges } = useMemo(
    () => generateLayout(MACHINE_FLOW),
    [MACHINE_FLOW]
  );

  const [nodes, setNodes, onNodesChange] = useNodesState(defaultNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(defaultEdges);
  const {
    machineStatusByBatch,
    setMachineStatusByBatch,
    activeFlows,
    setActiveFlows,
    simulationStarted,
    setSimulationStarted,
  } = useFactorySimulation();
  /* ---------------------- Animation & Flow Utilities ---------------------- */

  const activateFlowEdge = (from, to) => {
    const edgeId = `${from}->${to}`;
    setTimeout(() => {
      setActiveFlows((p) => new Set([...p, edgeId]));
      setTimeout(() => {
        setActiveFlows((p) => {
          const c = new Set(p);
          c.delete(edgeId);
          return c;
        });
      }, 2000);
    }, 250);
  };

  const setSingleActive = (batchMap, machine) => {
    const flow = whichFlow(machine);
    Object.keys(batchMap).forEach((m) => {
      const sameLine =
        (m.startsWith("Anode") && machine.startsWith("Anode")) ||
        (m.startsWith("Cathode") && machine.startsWith("Cathode")) ||
        (!m.startsWith("Anode") &&
          !m.startsWith("Cathode") &&
          !machine.startsWith("Anode") &&
          !machine.startsWith("Cathode"));
      if (sameLine) delete batchMap[m];
    });
    batchMap[machine] = "running";
  };

  const startBatchIfNew = (batchId) =>
    setMachineStatusByBatch((prev) =>
      prev[batchId]
        ? prev
        : {
            ...prev,
            [batchId]: {
              "Anode Mixing": "running",
              "Cathode Mixing": "running",
            },
          }
    );

  /* ----------------------------- Stage Advance ---------------------------- */

  const advanceWithinBatch = (batchId, completedMachine) => {
    setMachineStatusByBatch((prev) => {
      const next = structuredClone(prev);
      const batchMap = next[batchId] || {};
      const flow = whichFlow(completedMachine);
      const nextStage = nextOf(flow, completedMachine);

      const pairStages = (stage) => {
        if (stage.startsWith("Anode"))
          return [stage, stage.replace("Anode", "Cathode")];
        if (stage.startsWith("Cathode"))
          return [stage.replace("Cathode", "Anode"), stage];
        return [stage];
      };

      // Handle inspection merge
      if (isInspection(completedMachine)) {
        delete batchMap["Anode Inspection"];
        delete batchMap["Cathode Inspection"];

        setSingleActive(batchMap, "Rewinding");
        activateFlowEdge("Cathode Inspection", "Rewinding");

        next[batchId] = batchMap;
        return next;
      }

      // Electrode stages: run pairs together
      if (flow === ANODE_FLOW || flow === CATHODE_FLOW) {
        if (nextStage) {
          const [a, c] = pairStages(nextStage);

          // determine current stage's pair
          const [fromA, fromC] = pairStages(completedMachine);

          // activate flow from current stage to next stage
          activateFlowEdge(fromA, a);
          activateFlowEdge(fromC, c);

          setSingleActive(batchMap, a);
          setSingleActive(batchMap, c);
        }
        next[batchId] = batchMap;
        return next;
      }

      // Shared stages: single sequence
      if (flow === SHARED_FLOW) {
        delete batchMap[completedMachine];
        if (nextStage) {
          setSingleActive(batchMap, nextStage);
          activateFlowEdge(completedMachine, nextStage);
          next[batchId] = batchMap;
          return next;
        }
        delete next[batchId];
        return next;
      }

      next[batchId] = batchMap;
      return next;
    });
  };

  /* --------------------------- ReactFlow Updates -------------------------- */

  useEffect(() => {
    const merged = {};
    Object.values(machineStatusByBatch).forEach((b) => {
      Object.entries(b).forEach(([m, s]) => {
        if (s === "running") merged[m] = "running";
      });
    });
    setNodes((nds) =>
      nds.map((n) => ({
        ...n,
        data: { ...n.data, status: merged[n.id] || null, simulationStarted },
      }))
    );
  }, [machineStatusByBatch, simulationStarted, setNodes]);

  useEffect(() => {
    setEdges((eds) =>
      eds.map((e) => ({
        ...e,
        data: {
          ...e.data,
          isActive: activeFlows.has(e.id),
          showProgress: activeFlows.has(e.id),
        },
      }))
    );
  }, [activeFlows, setEdges]);

  useEffect(() => {
    if (animationTrigger) setSimulationStarted(true);
  }, [animationTrigger]);

  /* ------------------------------ WebSocket ------------------------------- */

  useEffect(() => {
    if (stageLog.length === 0) return;
    const latestLog = stageLog[stageLog.length - 1];
    const batchMatch = latestLog.match(/\(Batch (\d+)\)/);
    const batchId = batchMatch ? batchMatch[1] : null;
    if (!batchId) return;

    const findMachine = () => {
      for (const [proc, m] of Object.entries(processToMachineMap))
        if (latestLog.includes(proc)) return m;
      return null;
    };

    if (
      latestLog.includes("batch_requested") ||
      latestLog.includes("batch_started_processing")
    ) {
      startBatchIfNew(batchId);
      return;
    }
    /*
    if (latestLog.includes("machine_turned_off")) {
      const machine = findMachine();
      if (machine) advanceWithinBatch(batchId, machine);
      return;
    }
*/
    if (latestLog.includes("machine_turned_off")) {
      const machine = findMachine();
      if (machine) {
        advanceWithinBatch(batchId, machine);

        // 🔹 fallback: ensure shared stages never stop mid-flow
        if (machine === "Electrolyte Filling") {
          // if Formation Cycling log never appears, move forward automatically
          setTimeout(() => {
            advanceWithinBatch(batchId, "Formation Cycling");
          }, 800);
        }
      }
      return;
    }

    if (
      latestLog.includes("batch_completed") &&
      !latestLog.includes("batch_completed_anode_line") &&
      !latestLog.includes("batch_completed_cathode_line") &&
      !latestLog.includes("batch_completed_cell_line")
    ) {
      setMachineStatusByBatch((prev) => {
        const n = { ...prev };
        delete n[batchId];
        return n;
      });
      return;
    }
  }, [stageLog, processToMachineMap]);

  /* ------------------------------- Render -------------------------------- */

  const onNodeClick = useCallback(
    (_e, node) => setSelectedId(node.id),
    [setSelectedId]
  );

  return (
    <div style={{ width: "100%", height: "600px" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
      >
        <MiniMap />
        <Controls />
      </ReactFlow>
    </div>
  );
};

export default MachineFlowDiagram;
