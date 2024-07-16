import React from "react";
import PropTypes from "prop-types";

import "./Legend.css";

const Legend = ({ colorScale, percentileValues, title }) => {
  const levels = ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"];

  // Create a color block for each percentile value
  const colorBlocks = percentileValues.map((value, index) => (
    <div
      key={index}
      style={{
        backgroundColor: colorScale(value),
        width: `${100 / percentileValues.length}%`,
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
      <div className="value-labels" style={{ display: "flex", width: "100%" }}>
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
  percentileValues: PropTypes.arrayOf(PropTypes.number).isRequired,
  title: PropTypes.string.isRequired,
};

export default Legend;
