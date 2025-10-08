import React, { useContext } from "react";
import { WebSocketContext } from "../contexts/WebSocketContext";

export default function WebSocketControls() {
  const { clearLogs } = useContext(WebSocketContext);

  return (
    <div>
      <button onClick={clearLogs} className="clear-logs-button">
        Clear Logs
      </button>
    </div>
  );
}
