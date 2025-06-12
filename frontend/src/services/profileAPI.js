import axios from "axios";

// Determine API base URL based on environment
const getBaseUrl = () => {
  // Vercel environment or other production
  if (import.meta.env.PROD) {
    return 'https://mealmind-production.up.railway.app';
  }
  // For local development, use relative URL (proxy will handle it)
  return '';
};

// Create axios instance
const api = axios.create({
  baseURL: getBaseUrl(),
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: false, // Set to false to avoid CORS preflight issues
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
    });
    return Promise.reject(error);
  }
);

// Profile API service
const profileAPI = {
  setup: (data) => api.post("/api/profile/setup", data),
  post: (url, data) => api.post(url, data),
  get: () => api.get("/api/profile/get"),
  update: (data) => api.put("/api/profile/update", data),
};

export default profileAPI; 