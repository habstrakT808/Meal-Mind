// src/components/ui/Input.jsx
import React, { forwardRef } from "react";
import { motion } from "framer-motion";
import clsx from "clsx";

const Input = forwardRef(
  ({ label, error, icon, className, type = "text", ...props }, ref) => {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-2"
      >
        {label && (
          <label className="block text-sm font-semibold text-gray-700">
            {label}
          </label>
        )}

        <div className="relative">
          {icon && (
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span className="text-gray-400 w-5 h-5">{icon}</span>
            </div>
          )}

          <input
            ref={ref}
            type={type}
            className={clsx(
              "input-field",
              icon && "pl-10",
              error && "border-red-300 focus:border-red-500 focus:ring-red-200",
              className
            )}
            {...props}
          />
        </div>

        {error && (
          <motion.p
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-sm text-red-600"
          >
            {error}
          </motion.p>
        )}
      </motion.div>
    );
  }
);

Input.displayName = "Input";

export default Input;
