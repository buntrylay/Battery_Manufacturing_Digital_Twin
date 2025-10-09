import React, {
  createContext,
  useState,
  useEffect,
  useRef,
  useContext,
  useCallback,
} from "react";

// Create a context for sharing WebSocket data
export const WebSocketContext = createContext(null);
export const useLogs = () => useContext(WebSocketContext);

// Provider component to wrap the app and manage WebSocket connection
export const WebSocketProvider = ({ children }) => {
  // Store stage logs in state, initialize from localStorage if available
  const [stageLog, setStageLog] = useState(() => {
    const saved = localStorage.getItem("stageLog");
    return saved ? JSON.parse(saved) : [];
  });

  const socketRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);

  // Function to connect/reconnect to the WebSocket server, wrapped in useCallback
  const connectWebSocket = useCallback(() => {
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
      try {
        // Try to parse as JSON for machine notifications
        const data = JSON.parse(event.data);
        const batchInfo = data.data?.batch_id ? `(Batch ${data.data.batch_id}) ` : '';
        const formattedMessage = `[${data.timestamp ? new Date(data.timestamp).toLocaleTimeString() : new Date().toLocaleTimeString()}] ${batchInfo}${data.process_name || data.machine_id}: ${data.status} - ${data.data?.message || 'Status update'}`;
        
        setStageLog((prev) => {
          const updated = [...prev, formattedMessage];
          localStorage.setItem("stageLog", JSON.stringify(updated));
          return updated;
        });
      } catch (error) {
        // If not JSON, treat as plain text message
        setStageLog((prev) => {
          const updated = [...prev, event.data];
          localStorage.setItem("stageLog", JSON.stringify(updated));
          return updated;
        });
      }
    };

    // Attempt to reconnect after disconnect
    socket.onclose = () => {
      console.log("WebSocket disconnected, retrying in 5s...");
      // Pass the function reference directly to setTimeout
      reconnectTimeoutRef.current = setTimeout(connectWebSocket, 5000);
    };

    // Log errors and close the socket
    socket.onerror = (err) => {
      console.error("WebSocket error:", err);
      socket.close();
    };
  }, []); // Empty dependency array means this function is created only once

  // Function to clear logs from state and localStorage
  const clearLogs = () => {
    setStageLog([]);
    localStorage.removeItem("stageLog");
  };

  // Effect to establish WebSocket connection on mount and clean up on unmount
  useEffect(() => {
    // The connectWebSocket function is now a stable dependency
    connectWebSocket();
    return () => {
      if (socketRef.current) socketRef.current.close();
      if (reconnectTimeoutRef.current)
        clearTimeout(reconnectTimeoutRef.current);
    };
  }, [connectWebSocket]); // Add connectWebSocket to the dependency array

  const addLog = (message) => {
    setStageLog((prev) => {
      const updated = [...prev, message];
      localStorage.setItem("stageLog", JSON.stringify(updated));
      return updated;
    });
  };

  // Provide stageLog and clearLogs to children components
  return (
    <WebSocketContext.Provider value={{ stageLog, clearLogs, addLog }}>
      {children}
    </WebSocketContext.Provider>
  );
};
