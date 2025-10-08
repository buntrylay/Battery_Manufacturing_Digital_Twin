// services/api.js
import axios from "axios";

// Use environment variable or default to localhost
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";
export default API_URL;
// --- Corrected API Functions ---

/**
 * Starts the full simulation on the backend with anode and cathode parameters.
 * Uses the unified /api/simulation/start endpoint with mode="full".
 */
export const startSimulation = (data) => {
  const payload = {
    mode: "full",
    ...data
  };
  return axios.post(`${API_URL}/api/simulation/start`, payload);
};

/**
 * Starts mixing simulation for a specific electrode type using unified endpoint.
 */
export const startMixingSimulation = (data) => {
  const payload = {
    mode: "individual",
    stage: "mixing",
    ...data
  };
  return axios.post(`${API_URL}/api/simulation/start`, payload);
};

/**
 * Updates machine parameters via the generic parameter update endpoint.
 */
export const updateMachineParameters = (lineType, machineId, parameters) =>
  axios.patch(`${API_URL}/api/machine/${lineType}/${machineId}/parameters`, parameters);

/**
 * Generic function to start any machine simulation based on stage name.
 * Uses the unified /api/simulation/start endpoint.
 */
export const startMachineSimulation = async (stage, data) => {
  // Extract electrode_type and parameters from data
  const { electrode_type, ...parameters } = data;
  
  const payload = {
    mode: "individual",
    machine_type: stage,  // Backend expects machine_type, not stage
    parameters: parameters,
  };
  
  // Add electrode_type if provided
  if (electrode_type) {
    payload.electrode_type = electrode_type;
  }
  
  return axios.post(`${API_URL}/api/simulation/start`, payload);
};

/**
 * Start full factory simulation with all machine parameters using unified endpoint.
 * This replaces the original startSimulation function with enhanced capabilities.
 */
export const startFullSimulationUnified = (allParameters) => {
  const payload = {
    mode: "full",
    ...allParameters
  };
  
  return axios.post(`${API_URL}/api/simulation/start`, payload);
};

/**
 * Helper function to convert frontend form data to unified API format.
 * Takes inputs from all machines and formats them for the unified endpoint.
 */
export const formatForUnifiedAPI = (formData) => {
  const {
    anode_mixing = {},
    cathode_mixing = {},
    coating = {},
    drying = {},
    calendaring = {},
    slitting = {},
    inspection = {},
    rewinding = {},
    electrolyte_filling = {},
    formation_cycling = {},
    aging = {}
  } = formData;

  const payload = {
    mode: "full",
    anode_params: anode_mixing,
    cathode_params: cathode_mixing
  };

  // Add optional machine parameters if provided
  if (Object.keys(coating).length > 0) payload.coating_params = coating;
  if (Object.keys(drying).length > 0) payload.drying_params = drying;
  if (Object.keys(calendaring).length > 0) payload.calendaring_params = calendaring;
  if (Object.keys(slitting).length > 0) payload.slitting_params = slitting;
  if (Object.keys(inspection).length > 0) payload.inspection_params = inspection;
  if (Object.keys(rewinding).length > 0) payload.rewinding_params = rewinding;
  if (Object.keys(electrolyte_filling).length > 0) payload.electrolyte_filling_params = electrolyte_filling;
  if (Object.keys(formation_cycling).length > 0) payload.formation_cycling_params = formation_cycling;
  if (Object.keys(aging).length > 0) payload.aging_params = aging;

  return payload;
};

/**
 * Resets the simulation data on the backend.
 */
export const resetSimulation = () => axios.post(`${API_URL}/api/simulation/reset`);

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