// src/context/AuthContext.jsx
import React, { createContext, useContext, useState, useEffect } from "react";
import { authAPI } from "../utils/api";

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem("token"));

  // Initialize user from localStorage when component mounts
  useEffect(() => {
    const initAuth = () => {
      const savedToken = localStorage.getItem("token");
      const savedUser = localStorage.getItem("user");

      if (savedToken && savedUser) {
        // Initialize user state from localStorage
        const parsedUser = JSON.parse(savedUser);
        console.log("Auth initialized from localStorage:", {
          token: savedToken ? "exists" : "missing",
          user: parsedUser,
          has_profile: parsedUser.has_profile,
        });

        setUser(parsedUser);
        setToken(savedToken);
      }
    };

    initAuth();
  }, []);

  useEffect(() => {
    if (token) {
      localStorage.setItem("token", token);
      // Fetch current user data when token exists
      fetchCurrentUser();
    } else {
      localStorage.removeItem("token");
      setLoading(false);
    }
  }, [token]);

  const fetchCurrentUser = async () => {
    try {
      console.log(
        "Fetching current user with token:",
        token ? "exists" : "missing"
      );
      const response = await authAPI.getCurrentUser();

      // Log the response to help debug
      console.log("Current user response:", {
        user: response.data.user,
        has_profile: response.data.has_profile,
      });

      // Set user with has_profile included
      setUser({
        ...response.data.user,
        has_profile: response.data.has_profile,
      });

      // Also update localStorage
      localStorage.setItem(
        "user",
        JSON.stringify({
          ...response.data.user,
          has_profile: response.data.has_profile,
        })
      );
    } catch (error) {
      console.error("Failed to fetch current user:", error);
      // Token mungkin expired, logout
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      const response = await authAPI.login(credentials);
      const { access_token, user: userData, has_profile } = response.data;

      setToken(access_token);
      setUser({
        ...userData,
        has_profile: has_profile,
      });

      localStorage.setItem("token", access_token);
      localStorage.setItem(
        "user",
        JSON.stringify({
          ...userData,
          has_profile: has_profile,
        })
      );

      return response.data;
    } catch (error) {
      throw error;
    }
  };

  const signup = async (userData) => {
    try {
      const response = await authAPI.signup(userData);
      return response.data;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  };

  // Function untuk update profile status setelah setup
  const updateProfileStatus = () => {
    setUser((prev) => ({
      ...prev,
      has_profile: true,
    }));

    // Update localStorage juga
    const savedUser = localStorage.getItem("user");
    if (savedUser) {
      const userData = JSON.parse(savedUser);
      localStorage.setItem(
        "user",
        JSON.stringify({
          ...userData,
          has_profile: true,
        })
      );
    }
  };

  const value = {
    user,
    token,
    loading,
    login,
    signup,
    logout,
    updateProfileStatus,
    isAuthenticated: !!token,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
