import React from "react";
import PropTypes from "prop-types";

import "./Legend.css";

const Legend = ({ colorScale, minValue, maxValue, title }) => {
  const levels = ["Level 1", "Level 2", "Level 3", "Level 4", "Level 5"];
  const segmentCount = 5;
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
      <div className="value-labels">
        {Array.from({ length: segmentCount - 1 }, (_, i) => (
          <span key={i} className="value-label">
            {(minValue + step * (i + 1)).toFixed(2)}
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
  title: PropTypes.string.isRequired,
};

export default Legend;
