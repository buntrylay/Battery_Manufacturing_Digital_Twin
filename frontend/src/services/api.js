// services/api.js
import axios from "axios";

const API_URL = "http://localhost:8000";
export { API_URL };
export const startSimulations = (data) =>
  axios.post(`${API_URL}/start-both`, data);

export const downloadFile = (type) =>
  window.open(`${API_URL}/files/${type}`, "_blank");

export const downloadAll = () => window.open(`${API_URL}/files/all`, "_blank");
export const resetInputs = () => axios.post(`${API_URL}/reset`);
export const getLogs = () => axios.get(`${API_URL}/logs`);
export const getStatus = () => axios.get(`${API_URL}/status`);
export const getWebSocketURL = () => `${API_URL}/ws/status`;
// Fetch plot image for a process
export const getProcessPlot = async (processName) => {
  const response = await fetch(`${API_URL}/plots/process/${processName}`);
  if (!response.ok) {
    throw new Error("Failed to generate plot");
  }
  const blob = await response.blob();
  return URL.createObjectURL(blob); // returns a browser-safe object URL
};

// Same for summary plots (could be zip, but if you want image just fetch PNGs individually)
export const getMachinePlot = async (machineId) => {
  const response = await fetch(`${API_URL}/plots/machine/${machineId}`);
  if (!response.ok) {
    throw new Error("Failed to generate machine plot");
  }
  const blob = await response.blob();
  return URL.createObjectURL(blob);
};
