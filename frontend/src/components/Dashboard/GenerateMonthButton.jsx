import React, { useState } from "react";
import { toast } from "react-hot-toast";
import axios from "axios";
import { CalendarDaysIcon } from "@heroicons/react/24/outline";
import Button from "../ui/Button";

const GenerateMonthButton = ({ onSuccess }) => {
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerateMonth = async () => {
    try {
      setIsGenerating(true);

      const token = localStorage.getItem("token");
      const response = await axios.post(
        "http://127.0.0.1:5000/api/recommendations/generate_month_ahead",
        {},
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.data.status === "success") {
        toast.success(
          `Generated recommendations for the next ${response.data.created} days!`
        );
        if (onSuccess && typeof onSuccess === "function") {
          onSuccess();
        }
      }
    } catch (error) {
      console.error("Error generating month recommendations:", error);
      toast.error("Failed to generate recommendations for the month.");
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <Button
      onClick={handleGenerateMonth}
      isLoading={isGenerating}
      className="flex items-center space-x-2"
      variant="secondary"
    >
      <CalendarDaysIcon className="w-5 h-5" />
      <span>Generate Month Plan</span>
    </Button>
  );
};

export default GenerateMonthButton;
