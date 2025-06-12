// src/components/recommendations/MealCard.jsx
import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  ArrowPathIcon,
  FireIcon,
  ClockIcon,
  CheckCircleIcon,
} from "@heroicons/react/24/outline";
import Card from "../ui/Card";
import Button from "../ui/Button";
import {
  getFoodImage,
  checkImageAvailability,
  getPlaceholderImage,
} from "../../utils/foodImageHelper";

const MealCard = ({
  title,
  meal,
  onRegenerate,
  loading = false,
  completed = false,
  onMarkComplete,
}) => {
  const mealData = typeof meal === "string" ? JSON.parse(meal) : meal;
  const [foodImage, setFoodImage] = useState(null);
  const [imageLoaded, setImageLoaded] = useState(false);

  // Effect untuk mengambil gambar makanan berdasarkan nama
  useEffect(() => {
    const loadFoodImage = async () => {
      if (!mealData?.name) return;

      // Ambil gambar berdasarkan nama makanan
      const imageUrl = getFoodImage(mealData.name, title);

      // Periksa apakah gambar tersedia
      const isAvailable = await checkImageAvailability(imageUrl);

      // Set state gambar
      setFoodImage(isAvailable ? imageUrl : getFoodImage(null, title));
      setImageLoaded(true);
    };

    loadFoodImage();
  }, [mealData?.name, title]);

  return (
    <Card className="h-full">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center">
          <div
            className={`w-10 h-10 rounded-xl flex items-center justify-center mr-3 ${
              title === "Breakfast"
                ? "bg-yellow-100 text-yellow-600"
                : title === "Lunch"
                ? "bg-orange-100 text-orange-600"
                : "bg-purple-100 text-purple-600"
            }`}
          >
            {title === "Breakfast" ? "🌅" : title === "Lunch" ? "☀️" : "🌙"}
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{title}</h3>
            <p className="text-sm text-gray-500">
              {mealData?.calories || 0} calories
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

      <motion.div layout className="space-y-4">
        {/* Meal Image */}
        <div className="w-full h-40 bg-gradient-to-br from-gray-100 to-gray-200 rounded-xl overflow-hidden">
          {imageLoaded ? (
            <img
              src={foodImage}
              alt={mealData?.name || title}
              className="w-full h-full object-cover transition-opacity duration-300"
              onError={() => {
                // Jika gambar gagal dimuat, gunakan gambar default
                setFoodImage(getPlaceholderImage(title));
              }}
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <span className="text-4xl">{getPlaceholderImage(title)}</span>
            </div>
          )}
        </div>

        {/* Meal Details */}
        <div>
          <h4 className="font-medium text-gray-900 mb-2">
            {mealData?.name || "No meal selected"}
          </h4>

          <div className="flex items-center space-x-4 text-sm text-gray-500">
            <div className="flex items-center">
              <FireIcon className="w-4 h-4 mr-1" />
              {mealData?.calories || 0} cal
            </div>
            <div className="flex items-center">
              <ClockIcon className="w-4 h-4 mr-1" />
              15 min
            </div>
          </div>
        </div>

        {/* Nutrition Info */}
        {mealData?.protein && (
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="text-center p-2 bg-blue-50 rounded-lg">
              <div className="font-medium text-blue-600">
                {mealData.protein}g
              </div>
              <div className="text-blue-500">Protein</div>
            </div>
            <div className="text-center p-2 bg-green-50 rounded-lg">
              <div className="font-medium text-green-600">
                {mealData.carbs}g
              </div>
              <div className="text-green-500">Carbs</div>
            </div>
            <div className="text-center p-2 bg-yellow-50 rounded-lg">
              <div className="font-medium text-yellow-600">{mealData.fat}g</div>
              <div className="text-yellow-500">Fat</div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={onRegenerate}
            loading={loading}
            className="flex-1"
          >
            <ArrowPathIcon className="w-4 h-4" />
            Regenerate
          </Button>

          {!completed && onMarkComplete && (
            <Button size="sm" onClick={onMarkComplete} className="flex-1">
              Mark Done
            </Button>
          )}
        </div>
      </motion.div>
    </Card>
  );
};

export default MealCard;
