// src/pages/ProfileSetupPage.jsx
import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { toast } from "react-hot-toast";
import clsx from "clsx";
import axios from "axios";
import {
  UserIcon,
  ScaleIcon,
  SparklesIcon,
  ChevronRightIcon,
  ChevronLeftIcon,
  FireIcon,
  HeartIcon,
  XMarkIcon,
} from "@heroicons/react/24/outline";

import { profileAPI } from "../utils/api";
import { useAuth } from "../context/AuthContext";
import Button from "../components/ui/Button";
import Input from "../components/ui/Input";
import Select from "../components/ui/Select";
import Card from "../components/ui/Card";
import StepIndicator from "../components/ui/StepIndicator";

const ProfileSetupPage = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    weight: "",
    height: "",
    age: "",
    gender: "",
    activity_level: "",
    goal_weight: "",
    dietary_restrictions: [],
  });
  const [errors, setErrors] = useState({});
  const navigate = useNavigate();
  const { updateProfileStatus } = useAuth();

  const steps = [
    {
      title: "Basic Info",
      description: "Tell us about yourself",
      icon: <UserIcon className="w-6 h-6" />,
    },
    {
      title: "Physical Stats",
      description: "Your current measurements",
      icon: <ScaleIcon className="w-6 h-6" />,
    },
    {
      title: "Goals & Preferences",
      description: "What do you want to achieve?",
      icon: <HeartIcon className="w-6 h-6" />,
    },
  ];

  const genderOptions = [
    { value: "male", label: "Male" },
    { value: "female", label: "Female" },
  ];

  const activityLevelOptions = [
    { value: "sedentary", label: "Sedentary (Little to no exercise)" },
    { value: "light", label: "Light (Exercise 1-3 days/week)" },
    { value: "moderate", label: "Moderate (Exercise 3-5 days/week)" },
    { value: "active", label: "Active (Exercise 6-7 days/week)" },
    { value: "very_active", label: "Very Active (2x/day or intense exercise)" },
  ];

  const commonRestrictions = [
    "Dairy products",
    "Gluten",
    "Nuts",
    "Shellfish",
    "Eggs",
    "Soy",
    "Fish",
    "Beef",
    "Pork",
    "Chicken",
  ];

  const handleChange = (field, value) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));

    // Clear error when user starts typing
    if (errors[field]) {
      setErrors((prev) => ({
        ...prev,
        [field]: "",
      }));
    }
  };

  const handleRestrictionToggle = (restriction) => {
    setFormData((prev) => ({
      ...prev,
      dietary_restrictions: prev.dietary_restrictions.includes(restriction)
        ? prev.dietary_restrictions.filter((r) => r !== restriction)
        : [...prev.dietary_restrictions, restriction],
    }));
  };

  const validateStep = (step) => {
    const newErrors = {};

    if (step === 0) {
      if (!formData.age) newErrors.age = "Age is required";
      if (!formData.gender) newErrors.gender = "Gender is required";
    } else if (step === 1) {
      if (!formData.weight) newErrors.weight = "Weight is required";
      if (!formData.height) newErrors.height = "Height is required";
    } else if (step === 2) {
      if (!formData.activity_level)
        newErrors.activity_level = "Activity level is required";
      if (!formData.goal_weight)
        newErrors.goal_weight = "Goal weight is required";
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const nextStep = () => {
    if (validateStep(currentStep)) {
      setCurrentStep((prev) => Math.min(prev + 1, steps.length - 1));
    }
  };

  const prevStep = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 0));
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) return;

    setLoading(true);
    try {
      // Debug log to see what's being sent
      console.log("Sending profile data:", formData);

      // Convert string values to proper types
      const processedData = {
        weight: parseFloat(formData.weight),
        height: parseFloat(formData.height),
        age: parseInt(formData.age),
        gender: formData.gender,
        activity_level: formData.activity_level,
        goal_weight: formData.goal_weight
          ? parseFloat(formData.goal_weight)
          : parseFloat(formData.weight),
        dietary_restrictions: formData.dietary_restrictions || [],
      };

      console.log("Processed data:", processedData);

      // Use the setup method from profileAPI
      const response = await profileAPI.setup(processedData);

      console.log("Profile setup success:", response.data);

      // Update the user object to indicate profile has been set up
      updateProfileStatus();

      toast.success("Profile setup completed! 🎉");
      navigate("/dashboard");
    } catch (error) {
      console.error("Profile setup error:", error);

      // Display detailed error information
      if (error.response) {
        // Server responded with an error status
        console.log("Error data:", error.response.data);
        console.log("Error status:", error.response.status);
        console.log("Error headers:", error.response.headers);

        if (error.response.data?.error) {
          toast.error(error.response.data.error);
        } else {
          toast.error(`Server error: ${error.response.status}`);
        }
      } else if (error.request) {
        // Request was made but no response
        console.log("No response received:", error.request);
        toast.error("No response from server. Please try again.");
      } else {
        // Request setup error
        console.log("Error message:", error.message);
        toast.error(`Error: ${error.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-500 rounded-2xl flex items-center justify-center mx-auto mb-4 text-white">
                <UserIcon className="w-8 h-8" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Tell us about yourself
              </h2>
              <p className="text-gray-600">
                This helps us personalize your experience
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Age"
                type="number"
                value={formData.age}
                onChange={(e) => handleChange("age", e.target.value)}
                placeholder="25"
                error={errors.age}
                min="13"
                max="100"
              />

              <Select
                label="Gender"
                options={genderOptions}
                value={formData.gender}
                onChange={(e) => handleChange("gender", e.target.value)}
                placeholder="Select gender"
                error={errors.gender}
              />
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
              <div className="flex items-start">
                <SparklesIcon className="w-5 h-5 text-blue-500 mt-0.5 mr-3 flex-shrink-0" />
                <div className="text-sm text-blue-700">
                  <p className="font-medium mb-1">Why do we need this?</p>
                  <p>
                    Age and gender help us calculate your accurate calorie needs
                    using scientifically proven formulas.
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        );

      case 1:
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-gradient-to-r from-green-500 to-teal-500 rounded-2xl flex items-center justify-center mx-auto mb-4 text-white">
                <ScaleIcon className="w-8 h-8" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Your current measurements
              </h2>
              <p className="text-gray-600">
                Help us understand your starting point
              </p>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Input
                  label="Current Weight"
                  type="number"
                  value={formData.weight}
                  onChange={(e) => handleChange("weight", e.target.value)}
                  placeholder="70"
                  error={errors.weight}
                  min="30"
                  max="300"
                />
                <p className="text-xs text-gray-500 mt-1">in kilograms</p>
              </div>

              <div>
                <Input
                  label="Height"
                  type="number"
                  value={formData.height}
                  onChange={(e) => handleChange("height", e.target.value)}
                  placeholder="170"
                  error={errors.height}
                  min="100"
                  max="250"
                />
                <p className="text-xs text-gray-500 mt-1">in centimeters</p>
              </div>
            </div>

            {formData.weight && formData.height && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-green-50 border border-green-200 rounded-xl p-4"
              >
                <div className="text-center">
                  <p className="text-sm text-green-700 mb-2">
                    Your current BMI
                  </p>
                  <p className="text-2xl font-bold text-green-600">
                    {(formData.weight / (formData.height / 100) ** 2).toFixed(
                      1
                    )}
                  </p>
                  <p className="text-xs text-green-600">
                    {(() => {
                      const bmi =
                        formData.weight / (formData.height / 100) ** 2;
                      if (bmi < 18.5) return "Underweight";
                      if (bmi < 25) return "Normal weight";
                      if (bmi < 30) return "Overweight";
                      return "Obese";
                    })()}
                  </p>
                </div>
              </motion.div>
            )}
          </motion.div>
        );

      case 2:
        return (
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-gradient-to-r from-pink-500 to-rose-500 rounded-2xl flex items-center justify-center mx-auto mb-4 text-white">
                <HeartIcon className="w-8 h-8" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">
                Goals & Preferences
              </h2>
              <p className="text-gray-600">Let's customize your journey</p>
            </div>

            <Select
              label="Activity Level"
              options={activityLevelOptions}
              value={formData.activity_level}
              onChange={(e) => handleChange("activity_level", e.target.value)}
              placeholder="Select your activity level"
              error={errors.activity_level}
            />

            <Input
              label="Goal Weight"
              type="number"
              value={formData.goal_weight}
              onChange={(e) => handleChange("goal_weight", e.target.value)}
              placeholder="65"
              error={errors.goal_weight}
              min="30"
              max="300"
            />

            <div className="space-y-3">
              <label className="block text-sm font-semibold text-gray-700">
                Dietary Restrictions (Optional)
              </label>
              <p className="text-sm text-gray-500">
                Select any foods you want to avoid
              </p>

              <div className="grid grid-cols-2 gap-2">
                {commonRestrictions.map((restriction) => (
                  <motion.button
                    key={restriction}
                    type="button"
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => handleRestrictionToggle(restriction)}
                    className={clsx(
                      "p-3 rounded-xl border-2 transition-all duration-200 text-sm font-medium",
                      formData.dietary_restrictions.includes(restriction)
                        ? "border-primary-300 bg-primary-50 text-primary-700"
                        : "border-gray-200 bg-white text-gray-700 hover:border-gray-300"
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <span>{restriction}</span>
                      {formData.dietary_restrictions.includes(restriction) && (
                        <XMarkIcon className="w-4 h-4" />
                      )}
                    </div>
                  </motion.button>
                ))}
              </div>
            </div>

            {formData.dietary_restrictions.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="bg-yellow-50 border border-yellow-200 rounded-xl p-4"
              >
                <p className="text-sm text-yellow-700">
                  <span className="font-medium">Selected restrictions:</span>{" "}
                  {formData.dietary_restrictions.join(", ")}
                </p>
              </motion.div>
            )}
          </motion.div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 py-8 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-8"
        >
          <div className="flex justify-center mb-4">
            <div className="w-12 h-12 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-xl flex items-center justify-center">
              <SparklesIcon className="w-6 h-6 text-white" />
            </div>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Complete Your Profile
          </h1>
          <p className="text-gray-600">
            Help us create the perfect nutrition plan for you
          </p>
        </motion.div>

        {/* Step Indicator */}
        <StepIndicator steps={steps} currentStep={currentStep} />

        {/* Form Card */}
        <Card className="glass-effect">
          <AnimatePresence mode="wait">{renderStepContent()}</AnimatePresence>

          {/* Navigation Buttons */}
          <div className="flex justify-between items-center mt-8 pt-6 border-t border-gray-200">
            <Button
              variant="ghost"
              onClick={prevStep}
              disabled={currentStep === 0}
              className={currentStep === 0 ? "invisible" : ""}
            >
              <ChevronLeftIcon className="w-5 h-5" />
              Previous
            </Button>

            <div className="text-sm text-gray-500">
              Step {currentStep + 1} of {steps.length}
            </div>

            {currentStep < steps.length - 1 ? (
              <Button onClick={nextStep}>
                Next
                <ChevronRightIcon className="w-5 h-5" />
              </Button>
            ) : (
              <Button onClick={handleSubmit} loading={loading}>
                Complete Setup
                <SparklesIcon className="w-5 h-5" />
              </Button>
            )}
          </div>
        </Card>

        {/* Progress Bar */}
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
          className="h-2 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-full mt-8 mx-auto max-w-md"
          transition={{ duration: 0.5 }}
        />
      </div>
    </div>
  );
};

export default ProfileSetupPage;
