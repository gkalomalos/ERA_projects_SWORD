import React from "react";
import PropTypes from "prop-types";

import "./Legend.css";

const Legend = ({ colorScale, minValue, maxValue, percentileValues, title }) => {
  const levels = ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"];
  const segmentCount = 5; // Number of colored blocks
  const step = (maxValue - minValue) / (segmentCount - 1);

  const colorBlocks = Array.from({ length: segmentCount }, (_, i) => (
    <div
      key={i}
      style={{
        backgroundColor: colorScale(minValue + step * i),
        width: "20%",
        height: "20px",
      }}
    />
  ));

  return (
    <div className="legend-container">
      <div className="legend-title">{title}</div>
      <div className="color-blocks" style={{ display: "flex", width: "100%" }}>
        {colorBlocks}
      </div>
      <div className="value-labels" style={{ display: "flex", justifyContent: "space-between" }}>
        {/* Map over the percentileValues to create labels directly from these values */}
        {percentileValues.map((value, index) => (
          <span key={index} className="value-label">
            {value}
          </span>
        ))}
      </div>
      <div className="legend-labels">
        {levels.map((level, index) => (
          <div key={index} className="legend-label">
            {level}
          </div>
        ))}
      </div>
    </div>
  );
};

Legend.propTypes = {
  colorScale: PropTypes.func.isRequired,
  minValue: PropTypes.number.isRequired,
  maxValue: PropTypes.number.isRequired,
  percentileValues: PropTypes.arrayOf(PropTypes.number).isRequired,
  title: PropTypes.string.isRequired,
};

export default Legend;
