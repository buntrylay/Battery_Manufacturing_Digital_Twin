import React, { useState } from "react";
import "../styles/RealTimeDataPage.css";
import { useFlowPage } from "../contexts/FlowPageContext";
import { GrafanaMachineDisplay } from "../components/GrafanaMachineDisplay";
import { MACHINE_DASHBOARD_MAP } from "../helpers/DashboardTitles";
const GRAFANA_DASHBOARD_URL =
  process.env.REACT_APP_GRAFANA_DASHBOARD_URL || "http://localhost:3001/";

function RealTimeDataPage() {
  const { MACHINE_FLOW } = useFlowPage();
  let machineIds = MACHINE_FLOW.map((stage) => stage.id);

  let [selectedMachine, setMachineStage] = useState("Select a Machine");

  let handleMachineChange = (event) => {
    setMachineStage(event.target.value);
  };

  //Conditionally rendering the iframe based on machine selected
  const dashboardUid = MACHINE_DASHBOARD_MAP[selectedMachine];
  const dashboardSlug = dashboardUid ? dashboardUid.replace(/-uid/g, "") : null;
  const grafanaUrl = dashboardUid
    ? `${GRAFANA_DASHBOARD_URL}${dashboardUid}/${dashboardSlug}?orgId=1&kiosk`
    : null;
  return (
    <div className="realtime-page">
      <h2 className="page-title">Real-Time Data</h2>

      <div className="machine-select">
        <label htmlFor="machine">Select a Machine:</label>
        <select id="machine" onChange={handleMachineChange}>
          <option value="Select a Machine">-- Select a Machine --</option>
          {machineIds.map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>
      </div>
      <div>
        <h3>Live Data Visualization for {selectedMachine}</h3>
        {selectedMachine && (
          <>
            {grafanaUrl ? (
              <GrafanaMachineDisplay url={grafanaUrl} name={selectedMachine} />
            ) : (
              <p>Dashboard not available for this machine.</p>
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default RealTimeDataPage;
