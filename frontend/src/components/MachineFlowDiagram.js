// src/components/MachineFlowDiagram.js
import React, { useMemo, useEffect, useState } from "react";
import {
  ReactFlow,
  useNodesState,
  useEdgesState,
  Background,
  MiniMap,
  Controls,
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

const MachineFlowDiagram = ({ animationTrigger }) => {
  // Map backend process names to frontend machine IDs (defined at component top to avoid closure issues)
  const processToMachineMap = {
    // Mixing processes (exact backend names from PlantSimulation.py)
    'mixing_anode': 'Anode Mixing',
    'mixing_cathode': 'Cathode Mixing',
    
    // Coating processes (exact backend names from PlantSimulation.py)
    'coating_anode': 'Anode Coating',
    'coating_cathode': 'Cathode Coating',
    
    // Drying processes (exact backend names from PlantSimulation.py)
    'drying_anode': 'Anode Drying',
    'drying_cathode': 'Cathode Drying',
    
    // Calendaring processes (exact backend names from PlantSimulation.py)
    'calendaring_anode': 'Anode Calendaring',
    'calendaring_cathode': 'Cathode Calendaring',
    
    // Slitting processes (exact backend names from PlantSimulation.py)
    'slitting_anode': 'Anode Slitting',
    'slitting_cathode': 'Cathode Slitting',
    
    // Inspection processes (exact backend names from PlantSimulation.py)
    'inspection_anode': 'Anode Inspection',
    'inspection_cathode': 'Cathode Inspection',
    
    // Cell line processes (exact backend names from PlantSimulation.py)
    'rewinding_cell': 'Rewinding',
    'electrolyte_filling_cell': 'Electrolyte Filling',
    'formation_cycling_cell': 'Formation Cycling',
    'aging_cell': 'Aging',
    
    // Legacy/alternative names for backward compatibility
    'rewinding': 'Rewinding',
    'electrolyte_filling': 'Electrolyte Filling',
    'formation_cycling': 'Formation Cycling',
    'aging': 'Aging'
  };

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
  const [simulationStarted, setSimulationStarted] = useState(false);
  // eslint-disable-next-line no-unused-vars
  const [lastProcessSeen, setLastProcessSeen] = useState({});
  
  useEffect(() => {
    console.log("Updating nodes with status:", machineStatus, "simulationStarted:", simulationStarted);
    setNodes((nds) =>
      nds.map((node) => ({
        ...node,
        data: { 
          ...node.data, 
          status: machineStatus[node.id] || null,
          simulationStarted: simulationStarted
        },
      }))
    );
  }, [machineStatus, simulationStarted, setNodes]);

  // Handle animation trigger from parent component
  useEffect(() => {
    if (animationTrigger) {
      setSimulationStarted(true);
      
      // Reset process tracking
      setLastProcessSeen({});
      
      // Reset and start with first machines (Anode and Cathode Mixing)
      const initialStatus = {
        "Anode Mixing": "running",
        "Cathode Mixing": "running"
      };
      
      setMachineStatus(initialStatus);
      console.log("Animation triggered - Starting simulation with first machines:", initialStatus);
      
      // Force immediate node update
      setTimeout(() => {
        setNodes((nds) =>
          nds.map((node) => ({
            ...node,
            data: { 
              ...node.data, 
              status: initialStatus[node.id] || null,
              simulationStarted: true
            },
          }))
        );
      }, 100);
      
      // Add progressive startup animation for all edges
      setEdges((eds) =>
        eds.map((edge) => ({
          ...edge,
          animated: true,
          style: { stroke: '#007bff', strokeWidth: 2 }
        }))
      );
    }
  }, [animationTrigger, setEdges, setNodes]);

  // TODO: This listens for WebSocket logs and updates state
  useEffect(() => {
    if (stageLog.length === 0) {
      // Reset machine status when logs are cleared, but keep initial running state if simulation started
      setLastProcessSeen({}); // Reset process tracking
      if (simulationStarted) {
        setMachineStatus({
          "Anode Mixing": "running",
          "Cathode Mixing": "running"
        });
      } else {
        setMachineStatus({});
      }
      return;
    }
    
    const latestLog = stageLog[stageLog.length - 1];
    console.log("=== PROCESSING LATEST LOG ===");
    console.log("Raw log:", latestLog);
    console.log("All available machine IDs:", MACHINE_FLOW.map(m => m.id));
    console.log("Current machine status:", machineStatus);
    console.log("Process mapping available:", Object.keys(processToMachineMap));

    // NEW APPROACH: Direct completion detection from backend status messages
    // Based on actual WebSocket messages from the live logs
    const completionStatuses = [
      'mixing_completed', 'coating_completed', 'drying_completed', 
      'calendaring_completed', 'slitting_completed', 'inspection_completed',
      'rewinding_completed', 'electrolyte_filling_completed', 
      'formation_cycling_completed', 'aging_completed',
      'simulation_completed', 'completed', 'finished', 'done'
    ];
    
    const runningStatuses = [
      'mixing_started', 'coating_started', 'drying_started',
      'calendaring_started', 'slitting_started', 'inspection_started', 
      'rewinding_started', 'electrolyte_filling_started',
      'formation_cycling_started', 'aging_started',
      'running', 'simulation_started', 'simulation_progress'
    ];

    let detectedMachine = null;
    let detectedStatus = null;

    // SIMPLIFIED APPROACH: Only focus on machine completion (when turned off)
    // Check for "idle" status which indicates machine finished and turned off
    if (latestLog.includes(': idle -') && latestLog.includes('turned off')) {
      console.log("🛑 MACHINE TURNED OFF - Process completed");
      
      // Try to extract machine/process name from the message
      for (const [processName, machineName] of Object.entries(processToMachineMap)) {
        if (latestLog.includes(processName)) {
          detectedMachine = machineName;
          detectedStatus = 'completed';
          console.log("🎯 Machine completed and turned off:", processName, "->", machineName);
          break;
        }
      }
    }

    // Also check for explicit completion messages
    if (!detectedMachine) {
      for (const status of completionStatuses) {
        if (latestLog.includes(status)) {
          console.log("🏁 EXPLICIT COMPLETION DETECTED:", status);
          
          // Try to extract machine/process name from the message
          for (const [processName, machineName] of Object.entries(processToMachineMap)) {
            if (latestLog.includes(processName)) {
              detectedMachine = machineName;
              detectedStatus = 'completed';
              console.log("🎯 Explicit completion for:", processName, "->", machineName);
              break;
            }
          }
          
          if (detectedMachine) break;
        }
      }
    }

    // Also check for structured WebSocket message format: [timestamp] process_name: status - message
    if (!detectedMachine) {
      const structuredMatch = latestLog.match(/\[(.*?)\]\s+([^:]+):\s+([^-]+)\s*-\s*(.*)/);
      if (structuredMatch) {
        const [, timestamp, processOrMachine, status, message] = structuredMatch;
        console.log("📡 Structured message detected:", { processOrMachine, status, message });
        
        // Try to map the process/machine name
        const trimmedProcess = processOrMachine.trim();
        detectedMachine = processToMachineMap[trimmedProcess] || 
                         (MACHINE_FLOW.find(m => m.id.toLowerCase() === trimmedProcess.toLowerCase())?.id);
        
        if (detectedMachine) {
          // Check for exact backend status values
          const statusTrimmed = status.trim();
          
          if (completionStatuses.includes(statusTrimmed) || statusTrimmed === 'idle') {
            detectedStatus = 'completed';
          } else if (runningStatuses.includes(statusTrimmed) || statusTrimmed === 'running') {
            detectedStatus = 'running';
          }
          
          if (detectedStatus) {
            console.log("📡 Structured detection result:", trimmedProcess, "->", detectedMachine, "->", detectedStatus);
          }
        }
      }
    }

    // Apply the detected status change
    if (detectedMachine && detectedStatus) {
      console.log("📢 APPLYING STATUS CHANGE:", detectedMachine, "->", detectedStatus);
      
      // Check for aging completion - marks ALL machines as completed
      if (latestLog.includes('aging_completed') || latestLog.includes('Battery manufacturing finished!') || 
          (detectedMachine === 'Aging' && detectedStatus === 'completed')) {
        console.log("🎉 AGING COMPLETED - Marking all machines as completed (final state)");
        setMachineStatus(prevStatus => {
          const allCompleted = {};
          MACHINE_FLOW.forEach(machine => {
            allCompleted[machine.id] = 'completed';
          });
          console.log("🎊 Final state: All machines completed:", allCompleted);
          return allCompleted;
        });
        return;
      }

      // Handle machine completion and auto-progression
      if (detectedStatus === 'completed') {
        setMachineStatus(prevStatus => {
          const newStatus = { ...prevStatus };
          
          // Mark current machine as completed (blue)
          newStatus[detectedMachine] = 'completed';
          console.log("✅ Machine completed:", detectedMachine);
          
          // AUTO-PROGRESSION LOGIC: Start the next appropriate machine
          if (detectedMachine === 'Anode Mixing') {
            newStatus['Anode Coating'] = 'running';
            console.log("⏭️ Anode Mixing done → Starting Anode Coating");
          } else if (detectedMachine === 'Cathode Mixing') {
            newStatus['Cathode Coating'] = 'running';
            console.log("⏭️ Cathode Mixing done → Starting Cathode Coating");
          } else if (detectedMachine === 'Anode Coating') {
            newStatus['Anode Drying'] = 'running';
            console.log("⏭️ Anode Coating done → Starting Anode Drying");
          } else if (detectedMachine === 'Cathode Coating') {
            newStatus['Cathode Drying'] = 'running';
            console.log("⏭️ Cathode Coating done → Starting Cathode Drying");
          } else if (detectedMachine === 'Anode Drying') {
            newStatus['Anode Calendaring'] = 'running';
            console.log("⏭️ Anode Drying done → Starting Anode Calendaring");
          } else if (detectedMachine === 'Cathode Drying') {
            newStatus['Cathode Calendaring'] = 'running';
            console.log("⏭️ Cathode Drying done → Starting Cathode Calendaring");
          } else if (detectedMachine === 'Anode Calendaring') {
            newStatus['Anode Slitting'] = 'running';
            console.log("⏭️ Anode Calendaring done → Starting Anode Slitting");
          } else if (detectedMachine === 'Cathode Calendaring') {
            newStatus['Cathode Slitting'] = 'running';
            console.log("⏭️ Cathode Calendaring done → Starting Cathode Slitting");
          } else if (detectedMachine === 'Anode Slitting') {
            newStatus['Anode Inspection'] = 'running';
            console.log("⏭️ Anode Slitting done → Starting Anode Inspection");
          } else if (detectedMachine === 'Cathode Slitting') {
            newStatus['Cathode Inspection'] = 'running';
            console.log("⏭️ Cathode Slitting done → Starting Cathode Inspection");
          } else if (detectedMachine === 'Anode Inspection' || detectedMachine === 'Cathode Inspection') {
            // Check if BOTH inspections are complete before starting Rewinding
            const anodeComplete = (detectedMachine === 'Anode Inspection') || newStatus['Anode Inspection'] === 'completed';
            const cathodeComplete = (detectedMachine === 'Cathode Inspection') || newStatus['Cathode Inspection'] === 'completed';
            
            if (anodeComplete && cathodeComplete) {
              newStatus['Rewinding'] = 'running';
              console.log("🔗 Both inspections done → Starting Rewinding");
            }
          } else if (detectedMachine === 'Rewinding') {
            newStatus['Electrolyte Filling'] = 'running';
            console.log("⏭️ Rewinding done → Starting Electrolyte Filling");
          } else if (detectedMachine === 'Electrolyte Filling') {
            newStatus['Formation Cycling'] = 'running';
            console.log("⏭️ Electrolyte Filling done → Starting Formation Cycling");
          } else if (detectedMachine === 'Formation Cycling') {
            newStatus['Aging'] = 'running';
            console.log("⏭️ Formation Cycling done → Starting Aging");
          }
          // Aging completion is handled above to mark all machines as completed
          
          console.log("📊 Updated machine status:", newStatus);
          return newStatus;
        });
      }
      
      return; // Exit early since we handled the status update
    }
  }, [stageLog, MACHINE_FLOW, simulationStarted]);

  // Update edge animations based on machine status
  useEffect(() => {
    setEdges((eds) =>
      eds.map((edge) => {
        const sourceStatus = machineStatus[edge.source];
        const targetStatus = machineStatus[edge.target];

        // ACTIVE ANIMATION: Source completed → Target running (package moving)
        if (sourceStatus === "completed" && targetStatus === "running") {
          return { 
            ...edge, 
            type: "animated", 
            animated: true,
            data: { isActive: true, showProgress: true },
            style: { stroke: '#28a745', strokeWidth: 3 }
          };
        } 
        // STOP ANIMATION: Both machines completed (no more packages)
        else if (sourceStatus === "completed" && targetStatus === "completed") {
          return { 
            ...edge, 
            type: "default", 
            animated: false,
            data: { isActive: false, showProgress: false },
            style: { stroke: '#6c757d', strokeWidth: 2 } // Gray for completed path
          };
        }
        // DEFAULT: Simulation running but no active transfer
        else if (simulationStarted) {
          return { 
            ...edge, 
            type: "default", 
            animated: false,
            data: { isActive: false, showProgress: false },
            style: { stroke: '#007bff', strokeWidth: 2 }
          };
        } 
        // IDLE: Simulation not started
        else {
          return { 
            ...edge, 
            type: "default", 
            animated: false,
            data: { isActive: false, showProgress: false }
          };
        }
      })
    );
  }, [machineStatus, simulationStarted, setEdges]);

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
      <MiniMap/>
      <Controls />
      <Background color="#e6e3e3ff"  />
    </ReactFlow>
  );
};

export default MachineFlowDiagram;
