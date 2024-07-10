import { schemeReds, schemeBlues, schemeYlOrBr, schemeYlOrRd } from "d3-scale-chromatic";

const getColorScale = (hazard) => {
  const k = 9; // Index for accessing the largest set of colors, typically containing 9 colors
  switch (hazard) {
    case "flood":
      return schemeBlues[k].slice(-5); // Last 5 colors
    case "drought":
      return [...schemeYlOrBr[k]].reverse().slice(-5); // Reverse and then take the last 5 colors
    case "heatwaves":
      return schemeReds[k].slice(-5);
    default:
      return schemeYlOrRd[k].slice(-5);
  }
};

export const getScale = (hazard, maxValue, minValue) => {
  const colors = getColorScale(hazard);
  const range = maxValue - minValue;
  const segmentSize = range / colors.length; // Divide the range by the number of colors

  return (value) => {
    if (value === maxValue) return colors[colors.length - 1]; // Handle edge case for max value
    const index = Math.min(Math.floor((value - minValue) / segmentSize), colors.length - 1);
    return colors[index];
  };
};
