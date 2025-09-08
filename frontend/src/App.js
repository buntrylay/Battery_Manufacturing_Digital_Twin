// App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import { WebSocketProvider } from "./contexts/WebSocketContext";

// Styles
import "./styles/App.css";
import "./styles/Navbar.css";
import "./styles/Footer.css";
import "./styles/SimulationPage.css";
import "./styles/LogsPage.css";
import "./styles/TestingPage.css";

// Pages
import SimulationPage from "./pages/SimulationPage";
import LogsPage from "./pages/LogsPage";
import TestingPage from "./pages/TestingPage";
import FlowPage from "./pages/FlowPage";
import { FlowPageProvider } from "./contexts/FlowPageContext";
import RealTimeDataPage from "./pages/RealTimeDataPage";

export default function App() {
  return (
    <WebSocketProvider>
      <Router>
        <div className="App">
          <Navbar />
          <main className="App-main">
            <Routes>
              <Route
                path="/flow"
                element={
                  <FlowPageProvider>
                    <FlowPage />
                  </FlowPageProvider>
                }
              />
              <Route path="/" element={<SimulationPage />} />
              <Route path="/logs" element={<LogsPage />} />
              <Route path="/testing" element={<TestingPage />} />
              <Route path="/realtime" element={<RealTimeDataPage />} />
              <Route path="/404" element={<h1>PAGE NOT FOUND</h1>} />
              <Route path="*" element={<h1>PAGE NOT FOUND</h1>} />
            </Routes>
          </main>
          <Footer />
        </div>
      </Router>
    </WebSocketProvider>
  );
}

