import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { toast } from "react-hot-toast";
import { format, parseISO, isFuture } from "date-fns";
import {
  ArrowLeftIcon,
  CheckCircleIcon,
  XCircleIcon,
  FireIcon,
  ChevronRightIcon,
  ArrowPathIcon,
} from "@heroicons/react/24/outline";
import axios from "axios";

import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import MealCard from "../components/recommendations/MealCard";
import ActivityCard from "../components/recommendations/ActivityCard";

const DayDetailPage = () => {
  const { date } = useParams();
  const [loading, setLoading] = useState(true);
  const [recommendation, setRecommendation] = useState(null);
  const [checkin, setCheckin] = useState({
    food_completed: false,
    activity_completed: false,
  });
  const [isFutureDate, setIsFutureDate] = useState(false);
  const [creatingRecommendation, setCreatingRecommendation] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDayData();
  }, [date]);

  const fetchDayData = async () => {
    try {
      setLoading(true);

      // Validate date format first
      const parsedDate = parseISO(date);
      if (isNaN(parsedDate)) {
        toast.error("Invalid date format. Please use yyyy-MM-dd");
        navigate("/dashboard");
        return;
      }

      // Check if this is a future date
      setIsFutureDate(isFuture(parsedDate));

      const token = localStorage.getItem("token");

      const response = await axios.get(
        `http://127.0.0.1:5000/api/recommendations/day/${date}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setRecommendation(response.data.recommendation);

      if (response.data.checkin) {
        setCheckin(response.data.checkin);
      }
    } catch (error) {
      console.error("Error fetching day data:", error);
      // Only show toast if it's not a 404 error that we'll handle specially
      if (error.response?.status !== 404) {
        toast.error("Couldn't load data for this day");
      }
    } finally {
      setLoading(false);
    }
  };

  const createRecommendation = async () => {
    try {
      setCreatingRecommendation(true);

      const token = localStorage.getItem("token");

      const response = await axios.post(
        `http://127.0.0.1:5000/api/recommendations/generate_for_date`,
        { date: date },
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      setRecommendation(response.data.recommendation);
      toast.success("Created new recommendation for this day!");
    } catch (error) {
      console.error("Error creating recommendation:", error);
      toast.error("Failed to create recommendation");
    } finally {
      setCreatingRecommendation(false);
    }
  };

  const handleCheckInUpdate = async () => {
    try {
      const token = localStorage.getItem("token");

      await axios.post(
        `http://127.0.0.1:5000/api/recommendations/checkin/${recommendation.id}`,
        {
          food_completed: checkin.food_completed,
          activity_completed: checkin.activity_completed,
        },
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      );

      toast.success("Check-in updated successfully!");
    } catch (error) {
      console.error("Error updating checkin:", error);
      toast.error("Failed to update check-in status");
    }
  };

  const toggleCheckin = (type) => {
    setCheckin((prev) => ({
      ...prev,
      [type]: !prev[type],
    }));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center">
        <div className="text-center">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-gray-600">Loading day details...</p>
        </div>
      </div>
    );
  }

  if (!recommendation) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 p-4">
        <div className="max-w-3xl mx-auto">
          <Button onClick={() => navigate(-1)} variant="ghost" className="mb-4">
            <ArrowLeftIcon className="w-5 h-5 mr-1" /> Back
          </Button>

          <Card className="p-8">
            <div className="text-center">
              <h2 className="text-2xl font-bold mb-4">
                No Recommendation Found
              </h2>
              <p className="text-gray-600 mb-6">
                {isFutureDate
                  ? "This is a future date. Would you like to create a recommendation for this day?"
                  : "There's no recommendation data available for this day."}
              </p>

              {isFutureDate ? (
                <Button
                  onClick={createRecommendation}
                  disabled={creatingRecommendation}
                  className="flex items-center justify-center"
                >
                  {creatingRecommendation ? (
                    <>
                      <ArrowPathIcon className="w-5 h-5 mr-2 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    <>Create Recommendation</>
                  )}
                </Button>
              ) : (
                <Button onClick={() => navigate("/dashboard")}>
                  Go to Dashboard
                </Button>
              )}
            </div>
          </Card>
        </div>
      </div>
    );
  }

  const parsedDate = parseISO(date);
  const formattedDate = format(parsedDate, "EEEE, MMMM d, yyyy");

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 p-4">
      <div className="max-w-3xl mx-auto">
        <Button onClick={() => navigate(-1)} variant="ghost" className="mb-4">
          <ArrowLeftIcon className="w-5 h-5 mr-1" /> Back
        </Button>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <h1 className="text-3xl font-bold mb-2">{formattedDate}</h1>
          <p className="text-gray-600">
            Your nutrition and activity plan for this day.
          </p>
        </motion.div>

        {/* Completion Status */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="mb-6"
        >
          <Card>
            <div className="p-5">
              <h2 className="text-lg font-semibold mb-4">Day Progress</h2>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="food-completed"
                      className="w-5 h-5 text-primary-600 rounded"
                      checked={checkin.food_completed}
                      onChange={() => toggleCheckin("food_completed")}
                    />
                    <label
                      htmlFor="food-completed"
                      className="ml-2 text-gray-700 font-medium cursor-pointer"
                    >
                      Nutrition Plan Completed
                    </label>
                  </div>
                  {checkin.food_completed ? (
                    <CheckCircleIcon className="w-6 h-6 text-green-500" />
                  ) : (
                    <XCircleIcon className="w-6 h-6 text-gray-300" />
                  )}
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center">
                    <input
                      type="checkbox"
                      id="activity-completed"
                      className="w-5 h-5 text-primary-600 rounded"
                      checked={checkin.activity_completed}
                      onChange={() => toggleCheckin("activity_completed")}
                    />
                    <label
                      htmlFor="activity-completed"
                      className="ml-2 text-gray-700 font-medium cursor-pointer"
                    >
                      Activity Plan Completed
                    </label>
                  </div>
                  {checkin.activity_completed ? (
                    <CheckCircleIcon className="w-6 h-6 text-green-500" />
                  ) : (
                    <XCircleIcon className="w-6 h-6 text-gray-300" />
                  )}
                </div>
              </div>

              <div className="flex justify-end mt-4">
                <Button
                  onClick={handleCheckInUpdate}
                  className="flex items-center"
                >
                  Save Progress
                  <ChevronRightIcon className="w-5 h-5 ml-1" />
                </Button>
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Calorie Summary */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="mb-6"
        >
          <Card>
            <div className="p-5">
              <div className="flex items-center justify-between mb-2">
                <h2 className="text-lg font-semibold">Daily Calories</h2>
                <div className="flex items-center">
                  <FireIcon className="w-5 h-5 text-orange-500 mr-1" />
                  <span className="font-semibold">
                    {recommendation.total_calories} /{" "}
                    {recommendation.target_calories}
                  </span>
                </div>
              </div>

              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div
                  className="bg-gradient-to-r from-orange-500 to-amber-500 h-2.5 rounded-full"
                  style={{
                    width: `${Math.min(
                      (recommendation.total_calories /
                        recommendation.target_calories) *
                        100,
                      100
                    )}%`,
                  }}
                ></div>
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Meals */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-6"
        >
          <h2 className="text-xl font-bold mb-4">Meals</h2>

          <div className="space-y-4">
            <MealCard
              title="Breakfast"
              description={recommendation.breakfast}
              mealTime="7:00 - 9:00 AM"
              type="breakfast"
              isCompleted={checkin.food_completed}
            />

            <MealCard
              title="Lunch"
              description={recommendation.lunch}
              mealTime="12:00 - 2:00 PM"
              type="lunch"
              isCompleted={checkin.food_completed}
            />

            <MealCard
              title="Dinner"
              description={recommendation.dinner}
              mealTime="6:00 - 8:00 PM"
              type="dinner"
              isCompleted={checkin.food_completed}
            />
          </div>
        </motion.div>

        {/* Activities */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="mb-6"
        >
          <h2 className="text-xl font-bold mb-4">Activities</h2>

          <ActivityCard
            activities={recommendation.activities}
            isCompleted={checkin.activity_completed}
          />
        </motion.div>
      </div>
    </div>
  );
};

export default DayDetailPage;
