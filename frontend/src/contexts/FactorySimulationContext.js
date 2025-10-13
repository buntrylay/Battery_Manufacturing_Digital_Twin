import React, { createContext, useContext, useState } from "react";

const FactorySimulationContext = createContext(null);

export const useFactorySimulation = () => useContext(FactorySimulationContext);

export const FactorySimulationProvider = ({ children }) => {
  const [machineStatusByBatch, setMachineStatusByBatch] = useState({});
  const [activeFlows, setActiveFlows] = useState(new Set());
  const [simulationStarted, setSimulationStarted] = useState(false);

  return (
    <FactorySimulationContext.Provider
      value={{
        machineStatusByBatch,
        setMachineStatusByBatch,
        activeFlows,
        setActiveFlows,
        simulationStarted,
        setSimulationStarted,
      }}
    >
      {children}
    </FactorySimulationContext.Provider>
  );
};
