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
        type: "animated",
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
        type: "animated",
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
        type: "animated",
      });
    }
  });

  // Connect the final electrode stages to the first shared stage
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

const MachineFlowDiagram = ({ animationTrigger }) => {
  // Map backend process names to frontend machine IDs
  const processToMachineMap = useMemo(() => ({
    'mixing_anode': 'Anode Mixing',
    'mixing_cathode': 'Cathode Mixing',
    'coating_anode': 'Anode Coating',
    'coating_cathode': 'Cathode Coating',
    'drying_anode': 'Anode Drying',
    'drying_cathode': 'Cathode Drying',
    'calendaring_anode': 'Anode Calendaring',
    'calendaring_cathode': 'Cathode Calendaring',
    'slitting_anode': 'Anode Slitting',
    'slitting_cathode': 'Cathode Slitting',
    'inspection_anode': 'Anode Inspection',
    'inspection_cathode': 'Cathode Inspection',
    'rewinding_cell': 'Rewinding',
    'electrolyte_filling_cell': 'Electrolyte Filling',
    'formation_cycling_cell': 'Formation Cycling',
    'aging_cell': 'Aging',
  }), []);

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
  const [machineStatus, setMachineStatus] = useState(() => {
    const saved = localStorage.getItem("machineStatus");
    return saved ? JSON.parse(saved) : {};
  });
  const [simulationStarted, setSimulationStarted] = useState(() => {
    return localStorage.getItem("simulationRunning") === "true";
  });
  const [activeBatches, setActiveBatches] = useState(new Set()); // Track active batch IDs
  const [activeFlows, setActiveFlows] = useState(new Set()); // Track active package flows between machines

  // Persist machine status to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem("machineStatus", JSON.stringify(machineStatus));
  }, [machineStatus]);

  // Update nodes with machine status
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
      localStorage.setItem("simulationRunning", "true");
      
      // Start with mixing machines
      const initialStatus = {
        "Anode Mixing": "running",
        "Cathode Mixing": "running"
      };
      
      setMachineStatus(initialStatus);
      console.log("Animation triggered - Starting simulation with first machines:", initialStatus);
      
      // Activate edges for running flow
      setEdges((eds) =>
        eds.map((edge) => ({
          ...edge,
          data: { 
            ...edge.data, 
            isActive: true 
          }
        }))
      );
    }
  }, [animationTrigger, setEdges]);

  // WebSocket message processing for animations
  useEffect(() => {
    if (stageLog.length === 0) {
      // Reset when logs are cleared
      if (simulationStarted) {
        setMachineStatus({
          "Anode Mixing": "running",
          "Cathode Mixing": "running"
        });
      } else {
        setMachineStatus({});
        localStorage.removeItem("machineStatus");
        localStorage.removeItem("simulationRunning");
      }
      return;
    }
    
    const latestLog = stageLog[stageLog.length - 1];
    console.log("=== PROCESSING LATEST LOG ===");
    console.log("Raw log:", latestLog);

    let detectedMachine = null;
    let detectedStatus = null;
    let batchId = null;

    // Extract batch ID from log message (format: [time] (Batch X) machine: status)
    const batchMatch = latestLog.match(/\(Batch (\d+)\)/);
    if (batchMatch) {
      batchId = batchMatch[1];
    }

    // Look for machine turned off messages - these indicate BATCH processing completion
    if (latestLog.includes('machine_turned_off')) {
      // Extract machine name from the log
      for (const [processName, machineName] of Object.entries(processToMachineMap)) {
        if (latestLog.includes(processName)) {
          detectedMachine = machineName;
          detectedStatus = 'running'; // Turn machine green when it turns off (completes processing)
          console.log("� BATCH COMPLETED - Machine turning green:", processName, "->", machineName, "Batch:", batchId);
          break;
        }
      }
    }

    // SPECIAL HANDLING: Detect batch completion events
    if (latestLog.includes('batch_completed') && !latestLog.includes('batch_completed_anode_line') && !latestLog.includes('batch_completed_cathode_line') && !latestLog.includes('batch_completed_cell_line')) {
      console.log("🎉 FULL BATCH COMPLETED:", batchId);
      
      // Remove completed batch from active tracking
      if (batchId) {
        setActiveBatches(prev => {
          const updated = new Set(prev);
          updated.delete(batchId);
          
          // If no more active batches, show completion celebration
          if (updated.size === 0) {
            console.log("🏆 ALL BATCHES COMPLETED - Showing blue completion state!");
            setTimeout(() => {
              setMachineStatus(prevStatus => {
                const allCompleted = {};
                MACHINE_FLOW.forEach(machine => {
                  allCompleted[machine.id] = 'completed';
                });
                console.log("🔵 All machines now blue (completed state):", allCompleted);
                return allCompleted;
              });
              
              // Also clear active flows for clean completion state
              setActiveFlows(new Set());
            }, 500); // Quick transition to blue
          }
          
          return updated;
        });
      }
      return; // Exit early
    }

    // SPECIAL HANDLING: Detect new batches starting (batch_requested events)
    if (latestLog.includes('batch_requested') || latestLog.includes('batch_started_processing')) {
      console.log("🎯 NEW BATCH DETECTED - Reactivating mixing machines for batch:", batchId);
      
      // Track this batch
      if (batchId) {
        setActiveBatches(prev => new Set([...prev, batchId]));
      }
      
      // Reactivate mixing machines for new batch (keeping other machines in their current states)
      setMachineStatus(prevStatus => {
        const updatedStatus = { ...prevStatus };
        
        // Reactivate mixing machines from any state (idle, completed, or off)
        updatedStatus["Anode Mixing"] = "running";
        updatedStatus["Cathode Mixing"] = "running";
        
        console.log("� New batch - mixing machines reactivated, other machines continue:", updatedStatus);
        return updatedStatus;
      });
      
      return; // Exit early to avoid other processing
    }

    // Apply the detected status change
    if (detectedMachine && detectedStatus) {
      console.log("📢 APPLYING STATUS CHANGE:", detectedMachine, "->", detectedStatus, "Batch:", batchId);
      
      setMachineStatus(prevStatus => {
        const newStatus = { ...prevStatus };
        
        // For continuous batches: machines can be 'running' multiple times
        if (detectedStatus === 'running') {
          newStatus[detectedMachine] = 'running';
          console.log("🔥 Machine activated for batch:", detectedMachine, "Batch:", batchId);
        } else if (detectedStatus === 'idle') {
          // Mark as idle and prepare for next stage
          newStatus[detectedMachine] = 'idle';
          console.log("💤 Machine finished batch:", detectedMachine, "Batch:", batchId);
          
          // Auto-transition back to ready state after brief delay
          setTimeout(() => {
            setMachineStatus(prev => {
              const updated = { ...prev };
              if (updated[detectedMachine] === 'idle') {
                delete updated[detectedMachine]; // Clear to ready state
                console.log("🔄 Machine ready:", detectedMachine);
              }
              return updated;
            });
          }, 1000); // Shorter delay
          
          // SEQUENTIAL PROGRESSION: Only start next stage when current finishes
          // Max 2 green lights (anode + cathode pair) until inspection, then single progression
          const activateFlow = (fromMachine, toMachine, edgeId) => {
            console.log("📦 Package flowing:", fromMachine, "→", toMachine);
            
            // Small delay before showing package to prevent visual clutter
            setTimeout(() => {
              setActiveFlows(prev => new Set([...prev, edgeId]));
              
              // Remove package animation after 2 seconds
              setTimeout(() => {
                setActiveFlows(prev => {
                  const updated = new Set(prev);
                  updated.delete(edgeId);
                  return updated;
                });
              }, 2000);
            }, 300); // 300ms delay before package appears
          };

          // ELECTRODE LINE PROGRESSION (Anode + Cathode pairs)
          if (detectedMachine === 'Anode Mixing') {
            // Clear previous anode stages and start coating
            Object.keys(newStatus).forEach(key => {
              if (key.startsWith('Anode') && key !== 'Anode Mixing') {
                delete newStatus[key];
              }
            });
            newStatus['Anode Coating'] = 'running';
            activateFlow('Anode Mixing', 'Anode Coating', 'Anode Mixing->Anode Coating');
            console.log("⏭️ Anode: Mixing → Coating");
            
          } else if (detectedMachine === 'Cathode Mixing') {
            // Clear previous cathode stages and start coating
            Object.keys(newStatus).forEach(key => {
              if (key.startsWith('Cathode') && key !== 'Cathode Mixing') {
                delete newStatus[key];
              }
            });
            newStatus['Cathode Coating'] = 'running';
            activateFlow('Cathode Mixing', 'Cathode Coating', 'Cathode Mixing->Cathode Coating');
            console.log("⏭️ Cathode: Mixing → Coating");
            
          } else if (detectedMachine === 'Anode Coating') {
            newStatus['Anode Drying'] = 'running';
            activateFlow('Anode Coating', 'Anode Drying', 'Anode Coating->Anode Drying');
            console.log("⏭️ Anode: Coating → Drying");
            
          } else if (detectedMachine === 'Cathode Coating') {
            newStatus['Cathode Drying'] = 'running';
            activateFlow('Cathode Coating', 'Cathode Drying', 'Cathode Coating->Cathode Drying');
            console.log("⏭️ Cathode: Coating → Drying");
            
          } else if (detectedMachine === 'Anode Drying') {
            newStatus['Anode Calendaring'] = 'running';
            activateFlow('Anode Drying', 'Anode Calendaring', 'Anode Drying->Anode Calendaring');
            console.log("⏭️ Anode: Drying → Calendaring");
            
          } else if (detectedMachine === 'Cathode Drying') {
            newStatus['Cathode Calendaring'] = 'running';
            activateFlow('Cathode Drying', 'Cathode Calendaring', 'Cathode Drying->Cathode Calendaring');
            console.log("⏭️ Cathode: Drying → Calendaring");
            
          } else if (detectedMachine === 'Anode Calendaring') {
            newStatus['Anode Slitting'] = 'running';
            activateFlow('Anode Calendaring', 'Anode Slitting', 'Anode Calendaring->Anode Slitting');
            console.log("⏭️ Anode: Calendaring → Slitting");
            
          } else if (detectedMachine === 'Cathode Calendaring') {
            newStatus['Cathode Slitting'] = 'running';
            activateFlow('Cathode Calendaring', 'Cathode Slitting', 'Cathode Calendaring->Cathode Slitting');
            console.log("⏭️ Cathode: Calendaring → Slitting");
            
          } else if (detectedMachine === 'Anode Slitting') {
            newStatus['Anode Inspection'] = 'running';
            activateFlow('Anode Slitting', 'Anode Inspection', 'Anode Slitting->Anode Inspection');
            console.log("⏭️ Anode: Slitting → Inspection");
            
          } else if (detectedMachine === 'Cathode Slitting') {
            newStatus['Cathode Inspection'] = 'running';
            activateFlow('Cathode Slitting', 'Cathode Inspection', 'Cathode Slitting->Cathode Inspection');
            console.log("⏭️ Cathode: Slitting → Inspection");
            
          } else if (detectedMachine === 'Anode Inspection' || detectedMachine === 'Cathode Inspection') {
            // Check if this completes both electrode lines
            const updatedStatusWithCurrent = { ...newStatus, [detectedMachine]: 'idle' };
            const anodeInspectionDone = updatedStatusWithCurrent['Anode Inspection'] === 'idle';
            const cathodeInspectionDone = updatedStatusWithCurrent['Cathode Inspection'] === 'idle';
            
            if (anodeInspectionDone && cathodeInspectionDone && !newStatus['Rewinding']) {
              // Both electrode lines complete - merge to single cell line
              console.log("🔀 Both electrode inspections complete → Starting Rewinding");
              
              // Clear all electrode line statuses
              Object.keys(newStatus).forEach(key => {
                if (key.startsWith('Anode') || key.startsWith('Cathode')) {
                  delete newStatus[key];
                }
              });
              
              // Start single cell line progression
              newStatus['Rewinding'] = 'running';
              activateFlow(detectedMachine, 'Rewinding', `${detectedMachine}->Rewinding`);
              console.log("🔀 ELECTRODE LINES MERGED → Single cell line starts");
            } else {
              console.log("⏳ Waiting for both electrode lines to complete inspection...");
            }
            
          // SINGLE LINE PROGRESSION (Cell line - one at a time)
          } else if (detectedMachine === 'Rewinding') {
            // Clear all other cell line stages
            ['Electrolyte Filling', 'Formation Cycling', 'Aging'].forEach(stage => {
              delete newStatus[stage];
            });
            newStatus['Electrolyte Filling'] = 'running';
            activateFlow('Rewinding', 'Electrolyte Filling', 'Rewinding->Electrolyte Filling');
            console.log("⏭️ Cell: Rewinding → Electrolyte Filling");
            
          } else if (detectedMachine === 'Electrolyte Filling') {
            delete newStatus['Formation Cycling'];
            delete newStatus['Aging'];
            newStatus['Formation Cycling'] = 'running';
            activateFlow('Electrolyte Filling', 'Formation Cycling', 'Electrolyte Filling->Formation Cycling');
            console.log("⏭️ Cell: Electrolyte Filling → Formation Cycling");
            
          } else if (detectedMachine === 'Formation Cycling') {
            delete newStatus['Aging'];
            newStatus['Aging'] = 'running';
            activateFlow('Formation Cycling', 'Aging', 'Formation Cycling->Aging');
            console.log("⏭️ Cell: Formation Cycling → Aging");
          } else if (detectedMachine === 'Aging') {
            // One batch completed aging - this is the final step!
            console.log("🎉 Batch completed final aging stage! Batch:", batchId);
            
            // Don't automatically remove batch here - let batch_completed event handle it
            // This prevents premature completion detection
            console.log("� Aging complete, waiting for batch_completed event...");
          }
        }
        
        console.log("Updated machine status for continuous batches:", newStatus);
        return newStatus;
      });
    }
  }, [stageLog, processToMachineMap, simulationStarted]);

  // Update edges with active flow animations
  useEffect(() => {
    setEdges((eds) =>
      eds.map((edge) => ({
        ...edge,
        data: {
          ...edge.data,
          isActive: activeFlows.has(edge.id),
          showProgress: activeFlows.has(edge.id)
        }
      }))
    );
  }, [activeFlows, setEdges]);

  const onNodeClick = useCallback((event, node) => {
    console.log("Node clicked:", node.id);
    setSelectedId(node.id);
  }, [setSelectedId]);

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
        <Background variant="dots" gap={12} size={1} />
        <MiniMap />
        <Controls />
      </ReactFlow>
    </div>
  );
};

export default MachineFlowDiagram;
