// src/pages/DashboardPage.jsx
import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { toast } from "react-hot-toast";
import { useNavigate, Link } from "react-router-dom";
import {
  FireIcon,
  HeartIcon,
  TrophyIcon,
  ChartBarIcon,
  CalendarDaysIcon,
  UserIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  ClockIcon,
  CheckCircleIcon,
} from "@heroicons/react/24/outline";

import { useAuth } from "../context/AuthContext";
import { recommendationsAPI } from "../utils/api";
import MealCard from "../components/recommendations/MealCard";
import ActivityCard from "../components/recommendations/ActivityCard";
import StatsCard from "../components/recommendations/StatsCard";
import CalendarFeatures from "../components/Dashboard/CalendarFeatures";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import { profileAPI } from "../utils/api";

const DashboardPage = () => {
  const { user, logout } = useAuth();
  const [recommendations, setRecommendations] = useState(null);
  const [userStats, setUserStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState({});
  const [checkedIn, setCheckedIn] = useState({
    food: false,
    activity: false,
  });
  const [alreadyCheckedIn, setAlreadyCheckedIn] = useState(false);
  const [nextDayInfo, setNextDayInfo] = useState({
    date: null,
    willRegenerate: false,
  });
  const [programProgress, setProgramProgress] = useState({
    dayInProgram: 1,
    dietDuration: 30,
    daysRemaining: 29,
  });
  const [checkinStats, setCheckinStats] = useState({
    totalCompleted: 0,
    streak: 0,
    lastWeek: 0,
  });
  // Ref untuk melacak apakah notifikasi check-in sudah ditampilkan
  const checkinNotificationShown = useRef(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Check if there's a next-day recommendation from check-in
    const nextDayRecommendation = localStorage.getItem(
      "next_day_recommendation"
    );
    const nextDate = localStorage.getItem("next_date");
    const willRegenerate =
      localStorage.getItem("will_regenerate_tomorrow") === "true";

    if (nextDayRecommendation && nextDate) {
      try {
        const parsedRecommendation = JSON.parse(nextDayRecommendation);
        setRecommendations(parsedRecommendation);
        setNextDayInfo({
          date: new Date(nextDate),
          willRegenerate: willRegenerate,
        });

        // Show success message
        const dateFormatted = new Date(nextDate).toLocaleDateString("id-ID", {
          weekday: "long",
          year: "numeric",
          month: "long",
          day: "numeric",
        });

        toast.success(`Rekomendasi untuk ${dateFormatted} sudah siap!`);

        if (willRegenerate) {
          toast.success(
            "Rekomendasi telah disesuaikan berdasarkan aktivitas sebelumnya."
          );
        } else {
          toast.success("Semua aktivitas terpenuhi. Rekomendasi tetap sama.");
        }

        // Clear localStorage after using it
        localStorage.removeItem("next_day_recommendation");
        localStorage.removeItem("next_date");
        localStorage.removeItem("will_regenerate_tomorrow");

        // Extract user stats from recommendation
        if (parsedRecommendation.user_stats) {
          setUserStats(parsedRecommendation.user_stats);
        }

        setLoading(false);
      } catch (error) {
        console.error("Error parsing next day recommendation:", error);
        fetchRecommendations(); // Fallback to regular API call
      }
    } else {
      fetchRecommendations();
    }
  }, []);

  // Fungsi untuk mendapatkan data user yang lebih lengkap
  const refreshUserStats = async (skipFetchRecommendations = false) => {
    try {
      console.log("Refreshing user stats...");
      // Ambil data profil langsung
      const profileResponse = await profileAPI.get();
      const profile = profileResponse.data.profile;

      if (!profile) {
        console.error("Profile data not found");
        return;
      }

      console.log("Profile data retrieved:", profile);

      // Hitung BMR, TDEE, dan target kalori
      const bmr = calculateBMR(profile);
      const tdee = calculateTDEE(bmr, profile.activity_level);
      const targetCalories = calculateTargetCalories(profile, tdee);

      console.log("Calculated values:", { bmr, tdee, targetCalories });

      // Update userStats dengan nilai baru
      setUserStats((prevStats) => {
        const newStats = {
          ...prevStats,
          bmr: bmr,
          tdee: tdee,
          target_calories: targetCalories,
        };
        console.log("Updated userStats:", newStats);
        return newStats;
      });

      // Juga ambil data rekomendasi terbaru untuk memastikan sinkronisasi
      // Tetapi hanya jika skipFetchRecommendations = false
      if (!skipFetchRecommendations) {
        fetchRecommendations();
      }
    } catch (error) {
      console.error("Failed to refresh user stats:", error);
    }
  };

  // Perbaiki useEffect untuk mengambil data profil
  useEffect(() => {
    const fetchUserProfile = async () => {
      if (!user) return;
      refreshUserStats();
    };

    fetchUserProfile();
  }, [user]);

  const fetchRecommendations = async () => {
    try {
      const response = await recommendationsAPI.getToday();
      console.log("Today's recommendations:", response.data);

      setRecommendations(response.data.recommendations);

      // Jika ada data userStats dari backend, gabungkan dengan data yang dihitung
      if (response.data.user_stats) {
        const apiUserStats = response.data.user_stats;

        // Gabungkan data dari API dengan nilai yang dihitung
        setUserStats((prevStats) => {
          // Prioritaskan nilai yang sudah dihitung (jika ada)
          const newStats = {
            ...apiUserStats,
            bmr: prevStats?.bmr || apiUserStats.bmr,
            tdee: prevStats?.tdee || apiUserStats.tdee,
            target_calories:
              prevStats?.target_calories || apiUserStats.target_calories,
          };

          console.log("Combined userStats:", newStats);
          return newStats;
        });
      }

      // Periksa apakah user sudah melakukan check-in hari ini
      if (response.data.already_checked_in === true) {
        setAlreadyCheckedIn(true);
        // Jika sudah check-in, set checkbox food dan activity sebagai checked
        setCheckedIn({
          food: true,
          activity: true,
        });

        // Tampilkan toast informasi hanya jika belum ditampilkan sebelumnya
        if (!checkinNotificationShown.current) {
          toast.success("Anda sudah melakukan check-in untuk hari ini!");
          checkinNotificationShown.current = true;
        }
      }

      // Set program progress data
      if (response.data.program_progress) {
        setProgramProgress({
          dayInProgram: response.data.program_progress.day_in_program,
          dietDuration: response.data.program_progress.diet_duration,
          daysRemaining: response.data.program_progress.days_remaining,
        });
      }

      // Set checkin stats
      if (response.data.checkin_stats) {
        setCheckinStats({
          totalCompleted: response.data.checkin_stats.total_completed || 0,
          streak: response.data.checkin_stats.streak || 0,
          lastWeek: response.data.checkin_stats.last_week || 0,
        });
      }
    } catch (error) {
      console.error("Recommendations error:", error.response?.data);
      if (error.response?.data?.code === "PROFILE_NOT_FOUND") {
        toast.error("You need to set up your profile first");
        navigate("/profile-setup");
      } else {
        toast.error("Failed to fetch recommendations");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerate = async (type) => {
    setRegenerating({ ...regenerating, [type]: true });
    try {
      const response = await recommendationsAPI.regenerate(type);
      console.log("Regenerate response:", response.data);

      // Extract the regenerated item from the recommendations object
      let regeneratedItem;
      
      // Handle different response formats for meals vs activities
      if (type === "activities") {
        // For activities, we get the activities array directly
        regeneratedItem = response.data.recommendations.activities;
        console.log("Regenerated activities:", regeneratedItem);
      } else {
        // For meals (breakfast, lunch, dinner), we get a single object
        regeneratedItem = response.data.recommendations[type];
      }

      // Update state only if we got a valid response
      if (regeneratedItem) {
        setRecommendations((prev) => ({
          ...prev,
          [type]: regeneratedItem,
        }));

        toast.success(
          `${type.charAt(0).toUpperCase() + type.slice(1)} regenerated! 🎉`
        );
      } else {
        console.error("Invalid regenerate response format:", response.data);
        toast.error("Failed to process regenerated data");
      }
    } catch (error) {
      console.error("Regenerate error:", error.response?.data);
      toast.error("Failed to regenerate");
    } finally {
      setRegenerating({ ...regenerating, [type]: false });
    }
  };

  const handleCheckIn = async () => {
    try {
      const response = await recommendationsAPI.checkin({
        food_completed: checkedIn.food,
        activity_completed: checkedIn.activity,
      });

      setAlreadyCheckedIn(true);
      // Tandai bahwa notifikasi check-in sudah ditampilkan
      checkinNotificationShown.current = true;
      toast.success("Daily check-in completed! 🎉");

      // Segera perbarui data statistik setelah check-in
      // Lewati pemanggilan fetchRecommendations karena tidak perlu
      refreshUserStats(true);

      // Tidak perlu reload halaman, cukup perbarui data
    } catch (error) {
      console.error("Check-in error:", error);
      if (error.response?.data?.error === "Already checked in today") {
        setAlreadyCheckedIn(true);
        // Gunakan ref untuk mencegah notifikasi duplikat
        if (!checkinNotificationShown.current) {
          toast.error("Sudah melakukan check-in hari ini");
          checkinNotificationShown.current = true;
        }
      } else {
        toast.error("Check-in failed");
      }
    }
  };

  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return "Good Morning";
    if (hour < 17) return "Good Afternoon";
    return "Good Evening";
  };

  // Function untuk menghitung BMR
  const calculateBMR = (profile) => {
    if (
      !profile ||
      !profile.weight ||
      !profile.height ||
      !profile.age ||
      !profile.gender
    ) {
      return 0;
    }

    // Rumus Mifflin-St Jeor
    if (profile.gender.toLowerCase() === "male") {
      return Math.round(
        10 * profile.weight + 6.25 * profile.height - 5 * profile.age + 5
      );
    } else {
      return Math.round(
        10 * profile.weight + 6.25 * profile.height - 5 * profile.age - 161
      );
    }
  };

  // Function untuk menghitung TDEE
  const calculateTDEE = (bmr, activityLevel) => {
    if (!bmr || !activityLevel) return 0;

    const activityMultipliers = {
      sedentary: 1.2, // Little or no exercise
      light: 1.375, // Light exercise 1-3 days/week
      moderate: 1.55, // Moderate exercise 3-5 days/week
      active: 1.725, // Heavy exercise 6-7 days/week
      very_active: 1.9, // Very heavy exercise
    };

    return Math.round(bmr * (activityMultipliers[activityLevel] || 1.55));
  };

  // Function untuk menghitung target kalori
  const calculateTargetCalories = (profile, tdee) => {
    if (!profile || !profile.weight || !profile.goal_weight || !tdee) {
      return userStats?.target_calories || 0;
    }

    // Jika ingin menurunkan berat badan
    if (profile.goal_weight < profile.weight) {
      return Math.round(tdee - 500); // Defisit 500 kalori
    }
    // Jika ingin menaikkan berat badan
    else if (profile.goal_weight > profile.weight) {
      return Math.round(tdee + 300); // Surplus 300 kalori
    }
    // Jika ingin mempertahankan berat badan
    else {
      return tdee;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center">
        <div className="text-center">
          <div className="spinner mx-auto mb-4"></div>
          <p className="text-gray-600">
            Loading your personalized recommendations...
          </p>
        </div>
      </div>
    );
  }

  // Calculate program progress percentage
  const progressPercentage =
    (programProgress.dayInProgram / programProgress.dietDuration) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
      {/* Header */}
      <header className="bg-white/80 backdrop-blur-lg border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center">
                <svg
                  width="20"
                  height="20"
                  viewBox="0 0 32 32"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    d="M8 10L12 22M12 10L16 22M16 10L20 22M20 10L24 22"
                    stroke="white"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                  />
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">MealMind</h1>
                <p className="text-sm text-gray-500">
                  Your AI Nutrition Assistant
                </p>
              </div>
            </div>

            <div className="flex items-center space-x-3">
              <Link to="/profile">
                <Button variant="ghost" size="sm">
                  <Cog6ToothIcon className="w-5 h-5" />
                </Button>
              </Link>
              <CalendarFeatures />
              <Button variant="ghost" size="sm" onClick={logout}>
                <ArrowRightOnRectangleIcon className="w-5 h-5" />
              </Button>
              <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                <UserIcon className="w-5 h-5 text-gray-600" />
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Welcome Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            {getGreeting()}, {user?.username}! 👋
          </h2>

          {/* Program Progress Indicator */}
          <div className="flex items-center mb-3">
            <ClockIcon className="w-4 h-4 text-indigo-500 mr-2" />
            <span className="text-indigo-700 font-medium">
              Hari ke-{programProgress.dayInProgram} dari{" "}
              {programProgress.dietDuration} hari program diet
            </span>
            <span className="bg-indigo-100 text-indigo-800 text-xs font-medium px-2 py-0.5 rounded-full ml-3">
              {programProgress.daysRemaining} hari tersisa
            </span>
          </div>

          <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
            <div
              className="bg-gradient-to-r from-indigo-500 to-purple-600 h-2.5 rounded-full"
              style={{ width: `${Math.min(progressPercentage, 100)}%` }}
            ></div>
          </div>

          <p className="text-gray-600">
            Here's your personalized nutrition plan for today
          </p>

          {/* Next day info banner if coming from check-in */}
          {nextDayInfo.date && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`mt-4 p-4 rounded-lg ${
                nextDayInfo.willRegenerate
                  ? "bg-amber-50 border border-amber-200"
                  : "bg-green-50 border border-green-200"
              }`}
            >
              <p
                className={`${
                  nextDayInfo.willRegenerate
                    ? "text-amber-700"
                    : "text-green-700"
                } font-medium`}
              >
                {nextDayInfo.willRegenerate
                  ? "Ada aktivitas yang belum terpenuhi. Rekomendasi telah disesuaikan untuk tetap mencapai target diet."
                  : "Semua aktivitas terpenuhi! Rekomendasi untuk hari berikutnya tetap sama."}
              </p>
            </motion.div>
          )}
        </motion.div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <StatsCard
              icon={<FireIcon className="w-6 h-6" />}
              title="Target Calories"
              value={
                userStats?.target_calories
                  ? Math.round(userStats.target_calories)
                  : 0
              }
              subtitle="Daily goal"
              color="orange"
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <StatsCard
              icon={<HeartIcon className="w-6 h-6" />}
              title="BMR"
              value={userStats?.bmr ? Math.round(userStats.bmr) : 0}
              subtitle="Basal metabolic rate"
              color="pink"
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <StatsCard
              icon={<ChartBarIcon className="w-6 h-6" />}
              title="TDEE"
              value={userStats?.tdee ? Math.round(userStats.tdee) : 0}
              subtitle="Total daily expenditure"
              color="blue"
            />
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <StatsCard
              icon={<TrophyIcon className="w-6 h-6" />}
              title="Streak"
              value={checkinStats?.streak || 0}
              subtitle="Days consistent"
              color="green"
              trend={{ type: "up", value: `+${checkinStats?.lastWeek || 0}` }}
            />
          </motion.div>
        </div>

        {/* Main Content */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Meals Section */}
          <div className="lg:col-span-2">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="mb-6"
            >
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                <CalendarDaysIcon className="w-5 h-5 mr-2" />
                Today's Meals
              </h3>

              <div className="grid md:grid-cols-3 gap-6">
                <MealCard
                  title="Breakfast"
                  meal={recommendations?.breakfast}
                  onRegenerate={() => handleRegenerate("breakfast")}
                  loading={regenerating.breakfast}
                  completed={checkedIn.food}
                  onMarkComplete={() =>
                    setCheckedIn({ ...checkedIn, food: true })
                  }
                />

                <MealCard
                  title="Lunch"
                  meal={recommendations?.lunch}
                  onRegenerate={() => handleRegenerate("lunch")}
                  loading={regenerating.lunch}
                  completed={checkedIn.food}
                  onMarkComplete={() =>
                    setCheckedIn({ ...checkedIn, food: true })
                  }
                />

                <MealCard
                  title="Dinner"
                  meal={recommendations?.dinner}
                  onRegenerate={() => handleRegenerate("dinner")}
                  loading={regenerating.dinner}
                  completed={checkedIn.food}
                  onMarkComplete={() =>
                    setCheckedIn({ ...checkedIn, food: true })
                  }
                />
              </div>
            </motion.div>

            {/* Activities Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <h3 className="text-xl font-semibold text-gray-900 mb-4 flex items-center">
                💪 Today's Activities
              </h3>

              <ActivityCard
                activities={recommendations?.activities}
                onRegenerate={() => handleRegenerate("activities")}
                loading={regenerating.activities}
                completed={checkedIn.activity}
                onMarkComplete={() =>
                  setCheckedIn({ ...checkedIn, activity: true })
                }
              />
            </motion.div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Program Progress Card */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 }}
            >
              <Card>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Program Progress 📈
                </h3>

                <div className="space-y-4">
                  <div className="flex justify-between text-sm mb-1">
                    <span>Program Diet</span>
                    <span>
                      {programProgress.dayInProgram} dari{" "}
                      {programProgress.dietDuration} hari
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5 mb-2">
                    <div
                      className="bg-gradient-to-r from-purple-600 to-indigo-500 h-2.5 rounded-full"
                      style={{ width: `${Math.min(progressPercentage, 100)}%` }}
                    ></div>
                  </div>

                  <div className="pt-2 border-t border-gray-100">
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div className="p-2 bg-gray-50 rounded">
                        <p className="text-xl font-bold text-gray-700">
                          {programProgress.dayInProgram}
                        </p>
                        <p className="text-xs text-gray-500">Hari Sekarang</p>
                      </div>
                      <div className="p-2 bg-gray-50 rounded">
                        <p className="text-xl font-bold text-indigo-600">
                          {checkinStats.totalCompleted}
                        </p>
                        <p className="text-xs text-gray-500">Hari Selesai</p>
                      </div>
                      <div className="p-2 bg-gray-50 rounded">
                        <p className="text-xl font-bold text-green-600">
                          {programProgress.daysRemaining}
                        </p>
                        <p className="text-xs text-gray-500">Hari Tersisa</p>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            </motion.div>

            {/* Daily Check-in */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.7 }}
            >
              <Card>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Daily Check-in ✅
                </h3>

                {alreadyCheckedIn ? (
                  <div className="bg-green-50 rounded-lg p-4 flex items-center">
                    <CheckCircleIcon className="w-6 h-6 text-green-500 mr-2" />
                    <div>
                      <p className="text-green-700 font-medium">
                        Check-in selesai!
                      </p>
                      <p className="text-green-600 text-sm">
                        Anda sudah melakukan check-in untuk hari ini.
                      </p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={checkedIn.food}
                        onChange={(e) =>
                          setCheckedIn({ ...checkedIn, food: e.target.checked })
                        }
                        className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 mr-3"
                      />
                      <span className="text-gray-700">Completed meal plan</span>
                    </label>

                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={checkedIn.activity}
                        onChange={(e) =>
                          setCheckedIn({
                            ...checkedIn,
                            activity: e.target.checked,
                          })
                        }
                        className="rounded border-gray-300 text-primary-600 focus:ring-primary-500 mr-3"
                      />
                      <span className="text-gray-700">
                        Completed activities
                      </span>
                    </label>

                    <Button
                      onClick={handleCheckIn}
                      className="w-full"
                      disabled={
                        (!checkedIn.food && !checkedIn.activity) ||
                        alreadyCheckedIn
                      }
                    >
                      Submit Check-in
                    </Button>
                  </div>
                )}
              </Card>
            </motion.div>

            {/* Progress Summary */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.8 }}
            >
              <Card>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Today's Progress 📊
                </h3>

                <div className="space-y-4">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Calories</span>
                      <span>
                        {recommendations?.total_calories || 0} /{" "}
                        {recommendations?.target_calories || 0}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-green-500 to-teal-500 h-2 rounded-full"
                        style={{
                          width: `${Math.min(
                            ((recommendations?.total_calories || 0) /
                              (recommendations?.target_calories || 1)) *
                              100,
                            100
                          )}%`,
                        }}
                      />
                    </div>
                  </div>

                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Activities</span>
                      <span>
                        {checkedIn.activity || alreadyCheckedIn ? "100%" : "0%"}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full"
                        style={{
                          width:
                            checkedIn.activity || alreadyCheckedIn
                              ? "100%"
                              : "0%",
                        }}
                      />
                    </div>
                  </div>

                  {/* Streak info */}
                  <div className="pt-3 border-t border-gray-100 mt-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center">
                        <TrophyIcon className="w-4 h-4 text-yellow-500 mr-1" />
                        <span className="text-sm text-gray-600">
                          Current Streak
                        </span>
                      </div>
                      <span className="font-medium text-sm">
                        {checkinStats.streak} days
                      </span>
                    </div>
                  </div>
                </div>
              </Card>
            </motion.div>

            {/* Quick Tips */}
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.9 }}
            >
              <Card>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  💡 Today's Tip
                </h3>
                <p className="text-gray-600 text-sm">
                  Drink at least 8 glasses of water throughout the day to stay
                  hydrated and support your metabolism!
                </p>
              </Card>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
