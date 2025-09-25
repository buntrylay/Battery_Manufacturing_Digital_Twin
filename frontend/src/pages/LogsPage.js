import React, { useContext } from "react";
import { WebSocketContext, useLogs } from "../contexts/WebSocketContext";
import WebSocketControls from "../components/ResetButton";

function LogsPage() {
  const { stageLog } = useLogs();
  return (
    <div className="container">
      <WebSocketControls />
      <h2>Live Stage Updates</h2>
      <div className="stage-log">
        <ul>
          {stageLog.map((msg, idx) => (
            <li key={idx}>{msg}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default LogsPage;
