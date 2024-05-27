import React from "react";
import PropTypes from "prop-types";

import "./Legend.css";

const Legend = ({ colorScale, minValue, maxValue, title }) => {
  // Generate the CSS for the gradient
  const gradientCSS = `linear-gradient(to right, 
    ${colorScale(minValue)} 0%, 
    ${colorScale((minValue + maxValue) / 2)} 50%, 
    ${colorScale(maxValue)} 100%)`;

  const formatNumber = (num) => {
    return new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(num);
  };

  return (
    <div className="legend-container">
      <div className="legend-title">{title}</div>
      <div className="color-gradient" style={{ backgroundImage: gradientCSS }}>
        <div className="gradient-line"></div>
      </div>
      <div className="legend-values">
        {minValue === maxValue ? (
          <span>{formatNumber(minValue)}</span>
        ) : (
          <>
            <span>{formatNumber(minValue)}</span>
            <span>{formatNumber((minValue + maxValue) / 2)}</span>
            <span>{formatNumber(maxValue)}</span>
          </>
        )}
      </div>
    </div>
  );
};

Legend.propTypes = {
  colorScale: PropTypes.any.isRequired,
  minValue: PropTypes.number.isRequired,
  maxValue: PropTypes.number.isRequired,
  title: PropTypes.string.isRequired,
};

export default Legend;
