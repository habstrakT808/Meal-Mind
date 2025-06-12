import React from "react";
import DailyCalendar from "../Calendar/DailyCalendar";

const CalendarFeatures = () => {
  return (
    <div className="flex items-center">
      <DailyCalendar
        onSelectDay={(date, dayData) => {
          // This is handled internally in the component now
        }}
      />
    </div>
  );
};

export default CalendarFeatures;
