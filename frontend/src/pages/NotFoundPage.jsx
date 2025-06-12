// src/pages/NotFoundPage.jsx
import React from "react";
import { motion } from "framer-motion";
import { Link } from "react-router-dom";
import { HomeIcon, ArrowLeftIcon } from "@heroicons/react/24/outline";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";

const NotFoundPage = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center p-4">
      {/* Floating Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          animate={{
            y: [-20, 20, -20],
            rotate: [0, 180, 360],
          }}
          transition={{ duration: 8, repeat: Infinity }}
          className="absolute top-20 left-20 w-32 h-32 bg-primary-200 rounded-full opacity-20"
        />
        <motion.div
          animate={{
            y: [20, -20, 20],
            rotate: [360, 180, 0],
          }}
          transition={{ duration: 10, repeat: Infinity }}
          className="absolute bottom-20 right-20 w-40 h-40 bg-secondary-200 rounded-full opacity-20"
        />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-2xl w-full text-center relative z-10"
      >
        <Card className="glass-effect">
          {/* 404 Animation */}
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 200, delay: 0.2 }}
            className="mb-8"
          >
            <div className="text-8xl font-bold bg-gradient-to-r from-primary-500 to-secondary-500 bg-clip-text text-transparent">
              404
            </div>
          </motion.div>

          {/* Sad Food Emoji */}
          <motion.div
            animate={{
              rotate: [-5, 5, -5],
              scale: [1, 1.1, 1],
            }}
            transition={{ duration: 2, repeat: Infinity }}
            className="text-6xl mb-6"
          >
            🍽️💔
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="space-y-4 mb-8"
          >
            <h1 className="text-3xl font-bold text-gray-900">Page Not Found</h1>
            <p className="text-lg text-gray-600">
              Looks like this page went on a diet and disappeared!
            </p>
            <p className="text-gray-500">
              The page you're looking for doesn't exist or has been moved.
            </p>
          </motion.div>

          {/* Action Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <Link to="/">
              <Button size="lg" className="w-full sm:w-auto">
                <HomeIcon className="w-5 h-5" />
                Go to Home
              </Button>
            </Link>

            <Button
              variant="ghost"
              onClick={() => window.history.back()}
              size="lg"
              className="w-full sm:w-auto"
            >
              <ArrowLeftIcon className="w-5 h-5" />
              Go Back
            </Button>
          </motion.div>

          {/* Fun Facts */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="mt-8 pt-6 border-t border-gray-200"
          >
            <p className="text-sm text-gray-500 italic">
              "Fun fact: 404 errors burn 0 calories, but finding the right page
              is great exercise! 💪"
            </p>
          </motion.div>
        </Card>
      </motion.div>
    </div>
  );
};

export default NotFoundPage;
