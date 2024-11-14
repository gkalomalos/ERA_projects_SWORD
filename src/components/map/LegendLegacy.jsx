import React from "react";
import PropTypes from "prop-types";

import { formatNumberDivisor } from "../../utils/formatters";
import "./LegendLegacy.css";

const LegendLegacy = ({ colorScale, minValue, maxValue, type, unit }) => {
  const getSuffixAndDivisor = (value) => {
    if (value >= 1e9) return { suffix: "Billions", divisor: 1e9 };
    if (value >= 1e6) return { suffix: "Millions", divisor: 1e6 };
    if (value >= 1e3) return { suffix: "Thousands", divisor: 1e3 };
    return { suffix: "", divisor: 1 };
  };

  const updateLegendTitle = (unit, suffix) => {
    return `${type === "economic" ? "Asset Value" : "Number of People"} ${
      unit ? ` (${unit}${suffix ? ` in ${suffix}` : ""})` : ""
    }`;
  };

  const { suffix, divisor } = getSuffixAndDivisor(Math.max(Math.abs(minValue), Math.abs(maxValue)));
  const updatedTitle = updateLegendTitle(unit, suffix);

  // Generate the CSS for the gradient
  const gradientCSS = `linear-gradient(to right, 
    ${colorScale(minValue)} 0%, 
    ${colorScale((minValue + maxValue) / 2)} 50%, 
    ${colorScale(maxValue)} 100%)`;

  return (
    <div className="legend-container">
      <div className="legend-title">{updatedTitle}</div>
      <div className="color-gradient" style={{ backgroundImage: gradientCSS }}>
        <div className="gradient-line"></div>
      </div>
      <div className="legend-values">
        {minValue === maxValue ? (
          <span>{formatNumberDivisor(minValue, divisor)}</span>
        ) : (
          <>
            <span>{formatNumberDivisor(minValue, divisor)}</span>
            <span>{formatNumberDivisor((minValue + maxValue) / 2, divisor)}</span>
            <span>{formatNumberDivisor(maxValue, divisor)}</span>
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
  type: PropTypes.string.isRequired,
  unit: PropTypes.string.isRequired,
};

export default LegendLegacy;
