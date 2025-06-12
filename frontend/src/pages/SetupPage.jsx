import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import profileAPI from '../services/profileAPI';

const SetupPage = () => {
  const navigate = useNavigate();
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (values) => {
    setSubmitting(true);
    try {
      const response = await profileAPI.post("/api/profile/setup", values);
      
      if (response.status === 201) {
        toast.success("Profile setup successful!");
        navigate("/dashboard");
      }
    } catch (error) {
      console.error("Profile setup error:", error);
      
      if (error.response) {
        console.error("Error response data:", error.response.data);
        console.error("Error response status:", error.response.status);
        
        if (error.response.data && error.response.data.error) {
          toast.error(`Setup failed: ${error.response.data.error}`);
        } else {
          toast.error("Profile setup failed. Please try again.");
        }
      } else if (error.request) {
        console.error("Error request:", error.request);
        toast.error("Network error. Please check your connection.");
      } else {
        toast.error("Something went wrong. Please try again.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      {/* Render your form here */}
    </div>
  );
};

export default SetupPage; 