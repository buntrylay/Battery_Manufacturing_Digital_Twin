import React, { useContext } from "react";
import { WebSocketContext } from "../contexts/WebSocketContext";

function LogsPage() {
  const { stageLog } = useContext(WebSocketContext);

  return (
    <div className="container">
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
