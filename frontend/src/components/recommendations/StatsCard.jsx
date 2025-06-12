// src/components/recommendations/StatsCard.jsx
import React from "react";
import { motion } from "framer-motion";
import Card from "../ui/Card";

const StatsCard = ({ icon, title, value, subtitle, color = "blue", trend }) => {
  const colorClasses = {
    blue: "from-blue-500 to-blue-600",
    green: "from-green-500 to-green-600",
    purple: "from-purple-500 to-purple-600",
    orange: "from-orange-500 to-orange-600",
    pink: "from-pink-500 to-pink-600",
  };

  return (
    <Card className="h-full">
      <div className="flex items-center">
        <div
          className={`w-12 h-12 bg-gradient-to-r ${colorClasses[color]} rounded-xl flex items-center justify-center text-white mr-4`}
        >
          {icon}
        </div>
        <div className="flex-1">
          <p className="text-sm text-gray-500 mb-1">{title}</p>
          <div className="flex items-baseline">
            <motion.p
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="text-2xl font-bold text-gray-900"
            >
              {value}
            </motion.p>
            {trend && (
              <span
                className={`ml-2 text-sm ${
                  trend.type === "up"
                    ? "text-green-600"
                    : trend.type === "down"
                    ? "text-red-600"
                    : "text-gray-500"
                }`}
              >
                {trend.type === "up" ? "↗" : trend.type === "down" ? "↘" : "→"}{" "}
                {trend.value}
              </span>
            )}
          </div>
          {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
        </div>
      </div>
    </Card>
  );
};

export default StatsCard;
