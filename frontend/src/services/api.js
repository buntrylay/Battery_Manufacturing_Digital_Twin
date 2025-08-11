// services/api.js
import axios from "axios";

const API_URL = "http://localhost:8000";

export const startSimulations = (data) =>
  axios.post(`${API_URL}/start-both`, data);

export const downloadFile = (type) =>
  window.open(`${API_URL}/files/${type}`, "_blank");

export const downloadAll = () => window.open(`${API_URL}/files/all`, "_blank");
export const resetInputs = () => axios.post(`${API_URL}/reset`);
export const getLogs = () => axios.get(`${API_URL}/logs`);
export const getStatus = () => axios.get(`${API_URL}/status`);
export const getWebSocketURL = () => `${API_URL}/ws/status`;
