import React, { useState } from "react";
import "../styles/RealTimeDataPage.css";
import { useFlowPage } from "../contexts/FlowPageContext";
import { GrafanaMachineDisplay } from "../components/GrafanaMachineDisplay";
import { MACHINE_DASHBOARD_MAP } from "../helpers/DashboardTitles";
import ToggleSwitch from "../components/ToggleSwitch";
const GRAFANA_DASHBOARD_URL =
  process.env.REACT_APP_GRAFANA_DASHBOARD_URL || "http://localhost:3001/d/";

function RealTimeDataPage() {
  const { MACHINE_FLOW } = useFlowPage();
  const machineIds = MACHINE_FLOW.map((stage) => stage.id);

  const [selectedMachine, setMachineStage] = useState("Select a Machine");

  const handleMachineChange = (event) => {
    setMachineStage(event.target.value);
  };

  const dashboardUid = MACHINE_DASHBOARD_MAP[selectedMachine];
  const dashboardSlug = dashboardUid ? dashboardUid.replace(/-uid/g, "") : null;
  const grafanaUrl = dashboardUid
    ? `${GRAFANA_DASHBOARD_URL}${dashboardUid}/${dashboardSlug}?orgId=1&kiosk&from=now-30s&to=now&timezone=browser`
    : null;
  
  return (
    <div className="realtime-page">
      <h2 className="page-title">Real-Time Data</h2>
      <ToggleSwitch
        label="Quick Tips"
        infoContent={
          <>
            <p>
              Select a machine to see its updates. The Dashboard of the selected
              machine will show the results with a timeframe of 30 seconds.
            </p>
            <p>
              Extra information: Dashboards automatically update every 5
              seconds. To change timeframe either select "Last 30 seconds" or
              use the time range selector in the top right corner. You can
              refresh the dashboard or change machines at any time.
            </p>
          </>
        }
      />
      <div className="machine-select">
        <label htmlFor="machine">Select a Machine:</label>
        <select
          id="machine"
          onChange={handleMachineChange}
          value={selectedMachine}
        >
          <option value="Select a Machine">-- Select a Machine --</option>
          {machineIds.map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>
      </div>
      <div>
        {selectedMachine &&
          selectedMachine !== "Select a Machine" &&
          (grafanaUrl ? (
            <GrafanaMachineDisplay url={grafanaUrl} name={selectedMachine} />
          ) : (
            <p>Dashboard not available for this machine.</p>
          ))}
      </div>
    </div>
  );
}

export default RealTimeDataPage;
