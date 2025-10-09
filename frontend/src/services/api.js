// services/api.js
import axios from "axios";

// Use environment variable or default to localhost
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
export default API_URL;
// --- Corrected API Functions ---

/**
 * Starts the full simulation on the backend with anode and cathode parameters.
 * Updated to use the new /api/simulation/start endpoint.
 */
export const startSimulation = (data) =>
  axios.post(`${API_URL}/api/simulation/start`, data);

/**
 * Starts mixing simulation for a specific electrode type from flow page.
 */
export const startMixingSimulation = (data) =>
  axios.post(`${API_URL}/api/simulation/mixing/start`, data);

/**
 * Resets the simulation data on the backend.
 */
export const resetSimulation = () => axios.post(`${API_URL}/reset`);

/**
 * Returns the correct WebSocket URL for status updates.
 * NOTE: Replaces 'http' with 'ws'.
 */
export const getWebSocketURL = () => {
  const url = API_URL.replace(/^http/, "ws");
  return `${url}/ws/status`;
};

/**
 * A more robust function to download a file from the backend.
 * This handles errors and is not blocked by pop-up blockers.
 */
export const downloadFile = async (electrodeType) => {
  try {
    const response = await axios.get(`${API_URL}/files/${electrodeType}`, {
      responseType: "blob", // Important: tells axios to expect binary data
    });

    // Create a temporary link element to trigger the download
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;

    // Extract filename from response headers if available, otherwise fallback
    const contentDisposition = response.headers["content-disposition"];
    let fileName = `${electrodeType}_results.zip`; // fallback filename
    if (contentDisposition) {
      const fileNameMatch = contentDisposition.match(/filename="(.+)"/);
      if (fileNameMatch && fileNameMatch.length === 2) {
        fileName = fileNameMatch[1];
      }
    }

    link.setAttribute("download", fileName);
    document.body.appendChild(link);
    link.click();

    // Clean up the temporary link and object URL
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("File download failed:", error);
    // You can also show a user-friendly error message here
    alert(`Failed to download file for ${electrodeType}. Check the console for details.`);
  }
};

/**
 * Validate parameters for a specific stage using frontend field names.
 */
export const validateParameters = (stage, parameters) =>
  axios.post(`${API_URL}/api/parameters/validate`, { stage, parameters });

/**
 * Update machine parameters using frontend field names.
 */
export const updateParameters = (stage, parameters) =>
  axios.post(`${API_URL}/api/parameters/update`, { stage, parameters });

/**
 * Get current parameters for a machine stage.
 */
export const getCurrentParameters = (stage) =>
  axios.get(`${API_URL}/api/parameters/current/${encodeURIComponent(stage)}`);

/**
 * Get the current state of the plant simulation.
 */
export const getPlantState = () =>
  axios.get(`${API_URL}/api/simulation/state`);

/**
 * Reset the plant simulation.
 */
export const resetPlant = () =>
  axios.post(`${API_URL}/api/simulation/reset`);