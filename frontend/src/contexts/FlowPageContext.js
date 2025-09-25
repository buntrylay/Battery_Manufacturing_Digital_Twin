import React, { createContext, useState, useMemo, useContext } from "react";

export const FlowPageContext = createContext(null);

export const useFlowPage = () => useContext(FlowPageContext);

const MACHINE_FLOW_DATA = [
  // Cathode line
  { id: "Cathode Mixing", label: "Mixing" },
  { id: "Cathode Coating", label: "Coating" },
  { id: "Cathode Drying", label: "Drying" },
  { id: "Cathode Calendaring", label: "Calendaring" },
  { id: "Cathode Slitting", label: "Slitting" },
  { id: "Cathode Inspection", label: "Inspection" },

  // Anode line
  { id: "Anode Mixing", label: "Mixing" },
  { id: "Anode Coating", label: "Coating" },
  { id: "Anode Drying", label: "Drying" },
  { id: "Anode Calendaring", label: "Calendaring" },
  { id: "Anode Slitting", label: "Slitting" },
  { id: "Anode Inspection", label: "Inspection" },

  // Shared stages
  { id: "Rewinding", label: "Rewinding" },
  { id: "Electrolyte Filling", label: "Electrolyte Filling" },
  { id: "Formation Cycling", label: "Formation Cycling" },
  { id: "Aging", label: "Aging" },
];
//TODO: Replace with API call to fetch real data
export const FlowPageProvider = ({ children }) => {
  const [selectedId, setSelectedId] = useState(null);

  const selectedStage = useMemo(
    () => MACHINE_FLOW_DATA.find((m) => m.id === selectedId) || null,
    [selectedId]
  );

  const value = {
    MACHINE_FLOW: MACHINE_FLOW_DATA,
    selectedId,
    setSelectedId,
    selectedStage,
  };

  return (
    <FlowPageContext.Provider value={value}>
      {children}
    </FlowPageContext.Provider>
  );
};
