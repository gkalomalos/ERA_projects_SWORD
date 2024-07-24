import React from "react";
import PropTypes from "prop-types";

import "./LegendLegacy.css";

const LegendLegacy = ({ colorScale, minValue, maxValue, unit }) => {
  const getSuffixAndDivisor = (value) => {
    if (value >= 1e9) return { suffix: "Billions", divisor: 1e9 };
    if (value >= 1e6) return { suffix: "Millions", divisor: 1e6 };
    if (value >= 1e3) return { suffix: "Thousands", divisor: 1e3 };
    return { suffix: "", divisor: 1 };
  };

  const updateLegendTitle = (unit, suffix) => {
    return `Exposure${unit ? ` (${unit}${suffix ? ` in ${suffix}` : ""})` : ""}`;
  };

  const { suffix, divisor } = getSuffixAndDivisor(Math.max(Math.abs(minValue), Math.abs(maxValue)));
  const updatedTitle = updateLegendTitle(unit, suffix);

  // Generate the CSS for the gradient
  const gradientCSS = `linear-gradient(to right, 
    ${colorScale(minValue)} 0%, 
    ${colorScale((minValue + maxValue) / 2)} 50%, 
    ${colorScale(maxValue)} 100%)`;

  const formatNumber = (num) => {
    return new Intl.NumberFormat("en-US", { maximumFractionDigits: 2 }).format(num / divisor);
  };

  return (
    <div className="legend-container">
      <div className="legend-title">{updatedTitle}</div>
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

LegendLegacy.propTypes = {
  colorScale: PropTypes.func.isRequired,
  minValue: PropTypes.number.isRequired,
  maxValue: PropTypes.number.isRequired,
  unit: PropTypes.string.isRequired,
};

export default LegendLegacy;
