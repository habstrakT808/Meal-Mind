// src/components/ui/Card.jsx
import React from "react";
import { motion } from "framer-motion";
import clsx from "clsx";

const Card = ({
  children,
  className,
  hover = true,
  glass = false,
  gradient = false,
  ...props
}) => {
  const baseClasses =
    "rounded-2xl shadow-xl border border-gray-100 p-6 transition-all duration-300";

  const variants = {
    default: "bg-white",
    glass: "bg-white/80 backdrop-blur-lg border-white/20",
    gradient: "bg-gradient-to-br from-white to-primary-50",
  };

  const variantClass = glass
    ? variants.glass
    : gradient
    ? variants.gradient
    : variants.default;
  const hoverClass = hover ? "hover:shadow-2xl hover:-translate-y-1" : "";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={clsx(baseClasses, variantClass, hoverClass, className)}
      {...props}
    >
      {children}
    </motion.div>
  );
};

export default Card;
