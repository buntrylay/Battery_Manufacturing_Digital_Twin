import React, { useContext } from "react";
import { WebSocketContext } from "../contexts/WebSocketContext";

export default function WebSocketControls() {
  const { clearLogs } = useContext(WebSocketContext);

  return (
    <div>
      <button onClick={clearLogs}>Clear Logs</button>
    </div>
  );
}
