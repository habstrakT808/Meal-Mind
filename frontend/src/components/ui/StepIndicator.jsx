// src/components/ui/StepIndicator.jsx
import React from "react";
import { motion } from "framer-motion";
import { CheckIcon } from "@heroicons/react/24/outline";
import clsx from "clsx";

const StepIndicator = ({ steps, currentStep }) => {
  return (
    <div className="flex items-center justify-center mb-8">
      {steps.map((step, index) => (
        <div key={index} className="flex items-center">
          {/* Step Circle */}
          <motion.div
            initial={false}
            animate={{
              scale: currentStep === index ? 1.1 : 1,
              backgroundColor:
                currentStep > index
                  ? "#22c55e"
                  : currentStep === index
                  ? "#3b82f6"
                  : "#e5e7eb",
            }}
            className={clsx(
              "w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold transition-all duration-300",
              {
                "bg-green-500": currentStep > index,
                "bg-blue-500": currentStep === index,
                "bg-gray-300": currentStep < index,
              }
            )}
          >
            {currentStep > index ? (
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 500 }}
              >
                <CheckIcon className="w-6 h-6" />
              </motion.div>
            ) : (
              <span
                className={
                  currentStep === index ? "text-white" : "text-gray-500"
                }
              >
                {index + 1}
              </span>
            )}
          </motion.div>

          {/* Step Label */}
          <div className="ml-3 mr-8 hidden sm:block">
            <div
              className={clsx("text-sm font-medium", {
                "text-green-600": currentStep > index,
                "text-blue-600": currentStep === index,
                "text-gray-400": currentStep < index,
              })}
            >
              {step.title}
            </div>
            <div className="text-xs text-gray-500">{step.description}</div>
          </div>

          {/* Connector Line */}
          {index < steps.length - 1 && (
            <motion.div
              initial={false}
              animate={{
                backgroundColor: currentStep > index ? "#22c55e" : "#e5e7eb",
              }}
              className="h-0.5 w-12 mx-4 transition-all duration-300"
            />
          )}
        </div>
      ))}
    </div>
  );
};

export default StepIndicator;
