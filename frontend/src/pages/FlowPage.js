import React from "react";
import { useFlowPage } from "../contexts/FlowPageContext";
import SidePanel from "../components/SidePanel";
import "../styles/FlowPage.css";
import { stageDescriptions } from "../components/constants";

// Import machine images
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

const FlowPage = () => {
  const flowPageData = useFlowPage();
  if (!flowPageData) return <div>Loading...</div>;

  const { setSelectedId, selectedStage } = flowPageData;

  const cathodeStages = [
    { id: "Cathode Mixing", name: "Mixing", img: mixingImg },
    { id: "Cathode Coating", name: "Coating", img: coatingImg },
    { id: "Cathode Drying", name: "Drying", img: dryingImg },
    { id: "Cathode Calendaring", name: "Calendaring", img: calendaringImg },
    { id: "Cathode Slitting", name: "Slitting", img: slittingImg },
    { id: "Cathode Inspection", name: "Inspection", img: inspectionImg },
  ];

  const anodeStages = [
    { id: "Anode Mixing", name: "Mixing", img: mixingImg },
    { id: "Anode Coating", name: "Coating", img: coatingImg },
    { id: "Anode Drying", name: "Drying", img: dryingImg },
    { id: "Anode Calendaring", name: "Calendaring", img: calendaringImg },
    { id: "Anode Slitting", name: "Slitting", img: slittingImg },
    { id: "Anode Inspection", name: "Inspection", img: inspectionImg },
  ];

  const postInspection = [
    { id: "Rewinding", name: "Rewinding", img: rewindingImg },
    { id: "Electrolyte Filling", name: "Electrolyte Filling", img: electrolyteImg },
    { id: "Formation Cycling", name: "Formation Cycling", img: formationImg },
    { id: "Aging", name: "Aging", img: agingImg },
  ];

  const renderRowWithTitle = (title, stages) => (
    <div className="flow-group">
      <h3 className="flow-group-title">{title}</h3>
      <div className="flow-row">
        {stages.map((s) => (
          <div
            key={s.id}
            className="machine-node"
            onClick={() => setSelectedId(s.id)} // ✅ pass string ID
          >
            <img src={s.img} alt={s.name} />
            <p>{s.name}</p>

            <div className="machine-tooltip">
              {stageDescriptions[s.id] || "No description available"}
            </div>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className={`flow-layout ${selectedStage ? "with-panel" : "full"}`}>
      <div className="flow-canvas">
        {renderRowWithTitle("Cathode", cathodeStages)}
        {renderRowWithTitle("Anode", anodeStages)}
        {renderRowWithTitle("Cell Assembly & Aging", postInspection)}
      </div>
      {selectedStage && (
        <SidePanel
          selectedStage={selectedStage}
          onClose={() => setSelectedId(null)}
        />
      )}
    </div>
  );
};

export default FlowPage;
