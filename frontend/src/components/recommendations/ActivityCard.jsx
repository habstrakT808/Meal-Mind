// src/components/recommendations/ActivityCard.jsx
import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  ArrowPathIcon,
  FireIcon,
  ClockIcon,
  PlayIcon,
  CheckCircleIcon,
} from "@heroicons/react/24/outline";
import Card from "../ui/Card";
import Button from "../ui/Button";
import {
  getActivityImage,
  getActivityEmoji,
  checkImageAvailability,
} from "../../utils/activityImageHelper";

const ActivityCard = ({
  activities,
  onRegenerate,
  loading = false,
  completed = false,
  onMarkComplete,
}) => {
  const activitiesData =
    typeof activities === "string" ? JSON.parse(activities) : activities;
  const activityList = Array.isArray(activitiesData)
    ? activitiesData
    : [activitiesData];

  const [activityImages, setActivityImages] = useState({});
  const [imagesLoaded, setImagesLoaded] = useState({});

  // Effect untuk mengambil gambar aktivitas
  useEffect(() => {
    const loadActivityImages = async () => {
      const images = {};
      const loaded = {};

      for (const activity of activityList) {
        if (!activity?.name) continue;

        // Ambil gambar berdasarkan nama aktivitas
        const imageUrl = getActivityImage(activity.name);

        // Periksa apakah gambar tersedia
        const isAvailable = await checkImageAvailability(imageUrl);

        // Set state gambar
        images[activity.name] = isAvailable ? imageUrl : getActivityImage(null);
        loaded[activity.name] = true;
      }

      setActivityImages(images);
      setImagesLoaded(loaded);
    };

    if (activityList && activityList.length > 0) {
      loadActivityImages();
    }
  }, [activityList]);

  const getActivityIcon = (name) => {
    const activityName = name?.toLowerCase() || "";
    if (activityName.includes("jogging") || activityName.includes("running"))
      return "🏃‍♂️";
    if (activityName.includes("cycling") || activityName.includes("bersepeda"))
      return "🚴‍♂️";
    if (activityName.includes("swimming") || activityName.includes("berenang"))
      return "🏊‍♂️";
    if (activityName.includes("walking") || activityName.includes("jalan"))
      return "🚶‍♂️";
    if (activityName.includes("yoga")) return "🧘‍♀️";
    if (activityName.includes("gym") || activityName.includes("weight"))
      return "🏋️‍♂️";
    return "💪";
  };

  const totalCalories = activityList.reduce(
    (sum, activity) => sum + (activity?.calories_burned || 0),
    0
  );
  const totalDuration = activityList.reduce(
    (sum, activity) => sum + (activity?.duration_minutes || 0),
    0
  );

  return (
    <Card className="h-full">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <div className="w-10 h-10 bg-gradient-to-r from-green-500 to-teal-500 rounded-xl flex items-center justify-center mr-3 text-white">
            💪
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">Today's Activities</h3>
            <p className="text-sm text-gray-500">
              {totalCalories} calories • {totalDuration} minutes
            </p>
          </div>
        </div>

        {completed && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="text-green-500"
          >
            <CheckCircleIcon className="w-6 h-6" />
          </motion.div>
        )}
      </div>

      <div className="space-y-6">
        {activityList.length === 0 ? (
          <div className="py-8 text-center text-gray-500">
            No activities recommended yet
          </div>
        ) : (
          activityList.map((activity, index) => (
            <div
              key={index}
              className="border-b border-gray-100 pb-4 last:border-0"
            >
              <div className="flex items-start mb-3">
                <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mr-3 text-green-600 text-xl">
                  {getActivityIcon(activity.name)}
                </div>
                <div className="flex-1">
                  <h4 className="font-medium text-gray-900">{activity.name}</h4>
                  <div className="flex items-center text-sm text-gray-500">
                    <ClockIcon className="w-4 h-4 mr-1" />
                    {activity.duration_minutes} minutes
                    <span className="mx-2">•</span>
                    <FireIcon className="w-4 h-4 mr-1" />
                    {activity.calories_burned} calories
                  </div>
                  {activity.intensity && (
                    <span
                      className={`inline-block mt-2 text-xs px-2 py-1 rounded-full ${
                        activity.intensity === "high"
                          ? "bg-red-100 text-red-600"
                          : activity.intensity === "medium"
                          ? "bg-orange-100 text-orange-600"
                          : "bg-green-100 text-green-600"
                      }`}
                    >
                      {activity.intensity.charAt(0).toUpperCase() +
                        activity.intensity.slice(1)}{" "}
                      Intensity
                    </span>
                  )}
                </div>
              </div>

              {/* Activity Image */}
              <div className="rounded-xl overflow-hidden h-40 bg-gray-100">
                {imagesLoaded[activity.name] ? (
                  <img
                    src={activityImages[activity.name]}
                    alt={activity.name}
                    className="w-full h-full object-cover"
                    onError={() => {
                      // Jika gambar gagal dimuat, gunakan emoji sebagai fallback
                      setActivityImages((prev) => ({
                        ...prev,
                        [activity.name]: null,
                      }));
                      // Tambahkan kelas untuk menampilkan emoji di tengah
                      const imgElement = document.getElementById(
                        `activity-image-${index}`
                      );
                      if (imgElement) {
                        imgElement.style.display = "none";
                        imgElement.parentElement.classList.add(
                          "flex",
                          "items-center",
                          "justify-center"
                        );
                        imgElement.parentElement.innerHTML = `<span class="text-5xl">${getActivityEmoji(
                          activity.name
                        )}</span>`;
                      }
                    }}
                    id={`activity-image-${index}`}
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <span className="text-5xl">
                      {getActivityEmoji(activity.name)}
                    </span>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>

      <div className="pt-4 flex justify-between space-x-4">
        <Button
          variant="outline"
          size="sm"
          onClick={onRegenerate}
          loading={loading}
          className="flex-1"
        >
          <ArrowPathIcon className="w-4 h-4 mr-1" />
          Regenerate Activities
        </Button>

        {!completed && onMarkComplete && (
          <Button size="sm" onClick={onMarkComplete} className="flex-1">
            <CheckCircleIcon className="w-4 h-4 mr-1" />
            Mark Done
          </Button>
        )}
      </div>
    </Card>
  );
};

export default ActivityCard;
