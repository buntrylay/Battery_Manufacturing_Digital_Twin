// contexts/WebSocketContext.js
import React, { createContext, useState, useEffect, useRef } from "react";

export const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
  const [stageLog, setStageLog] = useState(() => {
    const saved = localStorage.getItem("stageLog");
    return saved ? JSON.parse(saved) : [];
  });

  const socketRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  const connectWebSocket = () => {
    if (socketRef.current) {
      socketRef.current.close();
    }

    const socket = new WebSocket("ws://localhost:8000/ws/status");
    socketRef.current = socket;

    socket.onopen = () => {
      console.log(" WebSocket connected");
    };

    socket.onmessage = (event) => {
      setStageLog((prev) => {
        const updated = [...prev, event.data];
        localStorage.setItem("stageLog", JSON.stringify(updated));
        return updated;
      });
    };

    socket.onclose = () => {
      console.log("WebSocket disconnected, retrying in 2s...");
      reconnectTimeoutRef.current = setTimeout(connectWebSocket, 2000);
    };

    socket.onerror = (err) => {
      console.error("WebSocket error:", err);
      socket.close();
    };
  };

  const clearLogs = () => {
    setStageLog([]);
    localStorage.removeItem("stageLog");
  };

  useEffect(() => {
    if (socketRef.current) return; // prevent reconnect on re-mount in dev

    connectWebSocket();

    return () => {
      if (socketRef.current) socketRef.current.close();
      if (reconnectTimeoutRef.current)
        clearTimeout(reconnectTimeoutRef.current);
    };
  }, []);

  return (
    <WebSocketContext.Provider value={{ stageLog, clearLogs }}>
      {children}
    </WebSocketContext.Provider>
  );
};
