import React, { useState, useEffect } from "react";
import Calendar from "react-calendar";
import { format } from "date-fns";
import { toast } from "react-hot-toast";
import axios from "axios";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import {
  ChevronLeftIcon,
  ChevronRightIcon,
  XMarkIcon,
  CalendarDaysIcon,
  CheckCircleIcon,
  XCircleIcon,
  InformationCircleIcon,
} from "@heroicons/react/24/outline";

import "react-calendar/dist/Calendar.css";
import "./calendar-styles.css"; // Custom styling

const DailyCalendar = ({ onSelectDay }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [value, setValue] = useState(new Date());
  const [monthData, setMonthData] = useState([]);
  const [selectedDayData, setSelectedDayData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Fetch current month's data when component mounts or month changes
  useEffect(() => {
    if (isOpen) {
      fetchMonthData(value);
    }
  }, [value, isOpen]);

  // Fetch recommendation data for the selected month
  const fetchMonthData = async (date) => {
    setLoading(true);
    try {
      const year = date.getFullYear();
      const month = date.getMonth() + 1;

      const token = localStorage.getItem("token");

      const response = await axios.get(
        `http://127.0.0.1:5000/api/recommendations/month/${year}/${month}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setMonthData(response.data.recommendations || []);
      setError(null);
    } catch (err) {
      console.error("Error fetching month data:", err);
      setError("Failed to load calendar data");
    } finally {
      setLoading(false);
    }
  };

  // Handle date selection
  const handleDateChange = (date) => {
    setValue(date);

    // Find data for selected day
    const selectedDate = format(date, "yyyy-MM-dd");
    const dayData = monthData.find((item) => item.date === selectedDate);

    setSelectedDayData(dayData);

    // Callback to parent component
    if (onSelectDay) {
      onSelectDay(date, dayData);
    }

    // Navigate to the day detail page
    navigate(`/day/${selectedDate}`);

    // Close the calendar
    setIsOpen(false);
  };

  // Determine tile class based on completion status
  const getTileClassName = ({ date, view }) => {
    if (view !== "month") return "";

    const dateStr = format(date, "yyyy-MM-dd");
    const dayData = monthData.find((item) => item.date === dateStr);

    if (!dayData) return "";

    // Check if day has checkins
    if (dayData.checkin) {
      const { food_completed, activity_completed } = dayData.checkin;
      if (food_completed && activity_completed) return "completed-day";
      if (food_completed || activity_completed) return "partial-day";
      return "incomplete-day";
    }

    return "no-data-day";
  };

  // Format day contents to add indicators
  const tileContent = ({ date, view }) => {
    if (view !== "month") return null;

    const dateStr = format(date, "yyyy-MM-dd");
    const dayData = monthData.find((item) => item.date === dateStr);

    if (!dayData) return null;

    return (
      <div className="daily-indicators">
        {dayData.checkin && (
          <>
            {dayData.checkin.food_completed && (
              <div
                className="indicator food-indicator"
                title="Food completed"
              ></div>
            )}
            {dayData.checkin.activity_completed && (
              <div
                className="indicator activity-indicator"
                title="Activity completed"
              ></div>
            )}
          </>
        )}
      </div>
    );
  };

  // Toggle calendar visibility
  const toggleCalendar = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="daily-calendar">
      {/* Calendar Toggle Button */}
      <button
        onClick={toggleCalendar}
        className="calendar-toggle flex items-center justify-center w-10 h-10 rounded-full bg-white hover:bg-gray-100 border border-gray-200 transition-colors"
        title="View Calendar"
      >
        <CalendarDaysIcon className="w-5 h-5 text-gray-700" />
      </button>

      {/* Calendar Modal */}
      <AnimatePresence>
        {isOpen && (
          <div className="fixed inset-0 flex items-center justify-center z-50">
            <div
              className="fixed inset-0 bg-black/50"
              onClick={toggleCalendar}
            ></div>

            <motion.div
              className="calendar-content"
              initial={{ scale: 0.9, y: 20, opacity: 0 }}
              animate={{ scale: 1, y: 0, opacity: 1 }}
              exit={{ scale: 0.9, y: 20, opacity: 0 }}
              transition={{ type: "spring", damping: 25 }}
            >
              {/* Close Button */}
              <button
                onClick={toggleCalendar}
                className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100"
              >
                <XMarkIcon className="w-5 h-5 text-gray-500" />
              </button>

              <div className="p-5">
                <h2 className="text-xl font-bold mb-4 text-gray-800">
                  Your Nutrition Calendar
                </h2>

                {/* Calendar Component */}
                <div className="calendar-wrapper">
                  <Calendar
                    onChange={handleDateChange}
                    value={value}
                    tileClassName={getTileClassName}
                    tileContent={tileContent}
                    prevLabel={<ChevronLeftIcon className="w-5 h-5" />}
                    nextLabel={<ChevronRightIcon className="w-5 h-5" />}
                    prev2Label={null}
                    next2Label={null}
                  />

                  {/* Legend */}
                  <div className="calendar-legend mt-3 flex items-center justify-center space-x-4 text-xs text-gray-600">
                    <div className="flex items-center">
                      <div className="w-3 h-3 rounded-full bg-green-500 mr-1"></div>
                      <span>Completed</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-3 h-3 rounded-full bg-yellow-500 mr-1"></div>
                      <span>Partial</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-3 h-3 rounded-full bg-red-500 mr-1"></div>
                      <span>Incomplete</span>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default DailyCalendar;
