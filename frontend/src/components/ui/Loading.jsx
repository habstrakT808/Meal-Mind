// src/components/ui/Loading.jsx
import React from "react";
import { motion } from "framer-motion";

const MealMindLogo = () => (
  <svg
    width="24"
    height="24"
    viewBox="0 0 32 32"
    xmlns="http://www.w3.org/2000/svg"
  >
    <rect width="32" height="32" rx="8" fill="currentColor" />
    <path
      d="M8 10L12 22M12 10L16 22M16 10L20 22M20 10L24 22"
      stroke="white"
      strokeWidth="2.5"
      strokeLinecap="round"
    />
  </svg>
);

const Loading = ({ message = "Loading...", fullScreen = false }) => {
  const containerClass = fullScreen
    ? "fixed inset-0 bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center z-50"
    : "flex items-center justify-center py-12";

  return (
    <div className={containerClass}>
      <div className="text-center">
        {/* Animated Logo */}
        <motion.div
          animate={{
            rotate: 360,
            scale: [1, 1.1, 1],
          }}
          transition={{
            rotate: { duration: 2, repeat: Infinity, ease: "linear" },
            scale: { duration: 1, repeat: Infinity, ease: "easeInOut" },
          }}
          className="w-16 h-16 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-2xl flex items-center justify-center mx-auto mb-6 text-white"
        >
          <MealMindLogo />
        </motion.div>

        {/* Loading Dots */}
        <div className="flex items-center justify-center space-x-2 mb-4">
          {[0, 1, 2].map((index) => (
            <motion.div
              key={index}
              animate={{
                scale: [1, 1.5, 1],
                opacity: [0.5, 1, 0.5],
              }}
              transition={{
                duration: 1,
                repeat: Infinity,
                delay: index * 0.2,
              }}
              className="w-3 h-3 bg-primary-500 rounded-full"
            />
          ))}
        </div>

        {/* Loading Message */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-gray-600 font-medium"
        >
          {message}
        </motion.p>
      </div>
    </div>
  );
};

export default Loading;
