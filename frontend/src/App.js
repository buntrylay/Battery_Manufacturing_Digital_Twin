// App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import { WebSocketProvider } from "./contexts/WebSocketContext";
import "./App.css";
// Pages
import SimulationPage from "./pages/SimulationPage";
import LogsPage from "./pages/LogsPage";
import TestingPage from "./pages/TestingPage";

export default function App() {
  return (
    <WebSocketProvider>
      <Router>
        <Navbar />
        <Routes>
          <Route path="/" element={<SimulationPage />} />
          <Route path="/logs" element={<LogsPage />} />
          <Route path="/testing" element={<TestingPage />} />
          {/* Catch-all route for 404 */}
          <Route path="/404" element={<h1>PAGE NOT FOUND</h1>} />
          <Route path="*" element={<h1>PAGE NOT FOUND</h1>} />
        </Routes>
        <Footer />
      </Router>
    </WebSocketProvider>
  );
}
