import axios from "axios";

// Determine API base URL based on environment
const getBaseUrl = () => {
  // If running in production on Railway
  if (window.location.hostname.includes('railway.app')) {
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
  withCredentials: true,
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
      headers: error.config?.headers,
    });

    // Handle 401 unauthorized errors
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api; 