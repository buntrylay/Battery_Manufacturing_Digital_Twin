import React, { createContext, useState, useMemo, useContext } from "react";

export const FlowPageContext = createContext(null);

// Custom hook for access to the context
export const useFlowPage = () => useContext(FlowPageContext);

const MACHINE_FLOW_DATA = [
  { id: "Mixing", label: "Mixing", group: "Mixing" },
  { id: "Coating", label: "Coating", group: "Coating" },
  { id: "Drying", label: "Drying", group: "Drying" },
  { id: "Calendaring", label: "Calendaring", group: "Calendaring" },
  { id: "Slitting", label: "Slitting", group: "Slitting" },
  { id: "Inspection", label: "Inspection", group: "Inspection" },
  { id: "Rewinding", label: "Rewinding", group: "Rewinding" },
  {
    id: "Electrolyte Filling",
    label: "Electrolyte Filling",
    group: "Electrolyte Filling",
  },
  {
    id: "Formation Cycling",
    label: "Formation Cycling",
    group: "Formation Cycling",
  },
  { id: "Aging", label: "Aging", group: "Aging" },
];

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
