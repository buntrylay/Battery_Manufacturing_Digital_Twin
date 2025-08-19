import React, {
  createContext,
  useState,
  useEffect,
  useRef,
  useContext,
} from "react";

// Create a context for sharing WebSocket data
export const WebSocketContext = createContext(null);
export const useLogs = () => useContext(WebSocketContext);

// Provider component to wrap the app and manage WebSocket connection
export const WebSocketProvider = ({ children }) => {
  // Store stage logs in state, initialize from localStorage if available
  const [stageLog, setStageLog, setLogs] = useState(() => {
    const saved = localStorage.getItem("stageLog");
    return saved ? JSON.parse(saved) : [];
  });
  const addLog = (message) => {
    setLogs((prev) => [...prev, message]);
  };
  const socketRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  // Function to connect/reconnect to the WebSocket server
  const connectWebSocket = () => {
    // Close any existing socket before reconnecting
    if (socketRef.current) {
      socketRef.current.close();
    }

    // Create a new WebSocket connection
    const socket = new WebSocket("ws://localhost:8000/ws/status");
    socketRef.current = socket;

    // Log when connection is established
    socket.onopen = () => {
      console.log(" WebSocket connection established");
    };

    // Handle incoming messages and update stageLog
    socket.onmessage = (event) => {
      setStageLog((prev) => {
        const updated = [...prev, event.data];
        localStorage.setItem("stageLog", JSON.stringify(updated));
        return updated;
      });
    };

    // Attempt to reconnect after disconnect
    socket.onclose = () => {
      console.log("WebSocket disconnected, retrying in 5s...");
      reconnectTimeoutRef.current = setTimeout(connectWebSocket, 5000);
    };

    // Log errors and close the socket
    socket.onerror = (err) => {
      console.error("WebSocket error:", err);
      socket.close();
    };
  };

  // Function to clear logs from state and localStorage
  const clearLogs = () => {
    setStageLog([]);
    localStorage.removeItem("stageLog");
  };

  // Effect to establish WebSocket connection on mount and clean up on unmount
  useEffect(() => {
    if (socketRef.current) return; // Prevent reconnect on re-mount in dev
    connectWebSocket();
    return () => {
      if (socketRef.current) socketRef.current.close();
      if (reconnectTimeoutRef.current)
        clearTimeout(reconnectTimeoutRef.current);
    };
  }, []);

  // Provide stageLog and clearLogs to children components
  return (
    <WebSocketContext.Provider value={{ stageLog, clearLogs, addLog }}>
      {children}
    </WebSocketContext.Provider>
  );
};
