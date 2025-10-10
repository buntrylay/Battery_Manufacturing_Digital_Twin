// App.js
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Footer from "./components/Footer";
import { WebSocketProvider } from "./contexts/WebSocketContext";
import { FactorySimulationProvider } from "./contexts/FactorySimulationContext";

// Styles
import "./styles/App.css";
import "./styles/Navbar.css";
import "./styles/Footer.css";
import "./styles/SimulationPage.css";
import "./styles/LogsPage.css";

// Pages
import LogsPage from "./pages/LogsPage";
import FlowPage from "./pages/FlowPage";
import { FlowPageProvider } from "./contexts/FlowPageContext";
import RealTimeDataPage from "./pages/RealTimeDataPage";

export default function App() {
  return (
    <WebSocketProvider>
      <FactorySimulationProvider>
        <Router>
          <div className="App">
            <Navbar />
            <main className="App-main">
              <Routes>
                <Route
                  path="/"
                  element={
                    <FlowPageProvider>
                      <FlowPage />
                    </FlowPageProvider>
                  }
                />
                <Route
                  path="/flow"
                  element={
                    <FlowPageProvider>
                      <FlowPage />
                    </FlowPageProvider>
                  }
                />
                <Route path="/logs" element={<LogsPage />} />
                <Route
                  path="/realtime"
                  element={
                    <FlowPageProvider>
                      <RealTimeDataPage />
                    </FlowPageProvider>
                  }
                />
                <Route path="/404" element={<h1>PAGE NOT FOUND</h1>} />
                <Route path="*" element={<h1>PAGE NOT FOUND</h1>} />
              </Routes>
            </main>
            <Footer />
          </div>
        </Router>
      </FactorySimulationProvider>
    </WebSocketProvider>
  );
}
