import React from "react";
import "./Legend.css"; // Make sure to include the CSS file for styling

const Legend = ({ colorScale }) => {
  // Generate gradient stops based on the colorScale prop
  const gradientCSS = `linear-gradient(to right, 
    ${colorScale(0)} 0%, 
    ${colorScale(0.5)} 50%, 
    ${colorScale(1)} 100%)`;

  return (
    <div className="legend-container">
      <div className="color-gradient" style={{ backgroundImage: gradientCSS }}></div>
      <div className="legend-values">
        <span>Low</span>
        <span>High</span>
      </div>
    </div>
  );
};

export default Legend;
