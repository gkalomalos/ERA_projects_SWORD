import React from "react";
import PropTypes from "prop-types";

import "./Legend.css";

const Legend = ({ colorScale, minValue, maxValue, title }) => {
  const segmentCount = 5; // Assuming you always have 5 colors
  const step = (maxValue - minValue) / (segmentCount - 1);

  const colorBlocks = Array.from({ length: segmentCount }, (_, i) => {
    const value = minValue + step * i;
    return (
      <div
        key={i}
        style={{
          backgroundColor: colorScale(value),
          width: "20%", // Makes each block take up 20% of the container
          height: "20px", // Set a fixed height for each color block
        }}
      />
    );
  });

  return (
    <div className="legend-container">
      <div className="legend-title">{title}</div>
      <div className="color-blocks" style={{ display: "flex", width: "100%" }}>
        {colorBlocks}
      </div>
      <div className="legend-values">
        <span>{minValue.toFixed(2)}</span>
        {Array.from({ length: segmentCount - 2 }, (_, i) => (
          <span key={i} style={{ flex: 1, textAlign: "center" }}>
            {(minValue + step * (i + 1)).toFixed(2)}
          </span>
        ))}
        <span>{maxValue.toFixed(2)}</span>
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
