import React from "react";

const MealMindLogo = ({ width = 20, height = 20, className = "" }) => {
  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 32 32"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      <path
        d="M8 10L12 22M12 10L16 22M16 10L20 22M20 10L24 22"
        stroke="currentColor"
        strokeWidth="2.5"
        strokeLinecap="round"
      />
    </svg>
  );
};

export default MealMindLogo;
