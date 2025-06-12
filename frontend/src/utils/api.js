// src/utils/api.js
import axios from "axios";

// Determine API base URL based on environment
const getBaseUrl = () => {
  // Use environment variable if available (Vercel deployment)
  if (import.meta.env.VITE_API_URL) {
    console.log("Using API URL from env:", import.meta.env.VITE_API_URL);
    return import.meta.env.VITE_API_URL;
  }
  // Fallback for production
  else if (import.meta.env.PROD) {
    console.log("Using fallback production API URL");
    return 'https://mealmind-production.up.railway.app';
  }
  // For local development, use relative URL (proxy will handle it)
  console.log("Using relative URL for development");
  return '';
};

// Create axios instance
const api = axios.create({
  baseURL: getBaseUrl(),
  headers: {
    "Content-Type": "application/json",
    "Accept": "application/json"
  },
  withCredentials: true, // Enable credentials for authentication
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle response errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.log("API Error:", {
      url: error.config?.url,
      status: error.response?.status,
      data: error.response?.data,
      message: error.message,
      baseURL: error.config?.baseURL
    });
    
    // Add more detailed logging for network errors
    if (!error.response) {
      console.error("Network Error Details:", {
        message: error.message,
        code: error.code,
        stack: error.stack
      });
    }
    
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  signup: (data) => api.post("/api/auth/signup", data),
  login: (data) => api.post("/api/auth/login", data),
  getCurrentUser: () => api.get("/api/auth/me"),
  testCors: () => api.get("/api/cors-test"),
};

// Profile API
export const profileAPI = {
  setup: (data) => api.post("/api/profile/setup", data),
  post: (url, data) => api.post(url, data),
  get: () => api.get("/api/profile/get"),
  update: (data) => api.put("/api/profile/update", data),
};

// Recommendations API
export const recommendationsAPI = {
  getToday: () => api.get("/api/recommendations/today"),
  regenerate: (type) => api.post(`/api/recommendations/regenerate/${type}`),
  checkin: (data) => api.post("/api/recommendations/checkin", data),
  getHistory: () => api.get("/api/recommendations/history"),
};

export default api;
