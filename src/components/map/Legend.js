import React from "react";
import "./Legend.css"; // Make sure to include the CSS file for styling

const Legend = ({ colorScale, minValue, maxValue }) => {
  // Generate the CSS for the gradient
  const gradientCSS = `linear-gradient(to right, 
    ${colorScale(minValue)} 0%, 
    ${colorScale((minValue + maxValue) / 2)} 50%, 
    ${colorScale(maxValue)} 100%)`;

  return (
    <div className="legend-container">
      <div className="color-gradient" style={{ backgroundImage: gradientCSS }}></div>
      <div className="legend-values">
        <span>{Math.round(minValue)}</span>
        <span>{Math.round(maxValue)}</span>
      </div>
    </div>
  );
};

export default Legend;
