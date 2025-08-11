// contexts/WebSocketContext.js
import React, { createContext, useState, useEffect } from "react";

export const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
  const [stageLog, setStageLog] = useState([]);

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/ws/status");

    socket.onmessage = (event) => {
      setStageLog((prev) => [...prev, event.data]);
    };

    socket.onclose = () => console.log("WebSocket disconnected");

    return () => socket.close();
  }, []);

  return (
    <WebSocketContext.Provider value={{ stageLog }}>
      {children}
    </WebSocketContext.Provider>
  );
};
