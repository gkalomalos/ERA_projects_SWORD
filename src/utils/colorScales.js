import { schemeReds, schemeBlues, schemeYlOrBr, schemeYlOrRd } from "d3-scale-chromatic";

const getColorScale = (hazard) => {
  const k = 9; // Index for accessing the largest set of colors, typically containing 9 colors
  switch (hazard) {
    case "flood":
      return schemeBlues[k].slice(-5); // Last 5 colors
    case "drought":
      return [...schemeYlOrBr[k]].slice(-5);
    case "heatwaves":
      return schemeReds[k].slice(-5);
    default:
      return schemeYlOrRd[k].slice(-5);
  }
};

export const getScale = (hazard, percentileValues) => {
  const colors = getColorScale(hazard);
  const minValue = Math.min(...percentileValues);
  const maxValue = Math.max(...percentileValues);
  const range = maxValue - minValue;
  // Adding a very small value to range can help to include the maximum value in the calculations.
  const segmentSize = range / (colors.length - 1); // Divide the range exactly by the number of colors minus one.

  return (value) => {
    if (value >= maxValue) return colors[colors.length - 1]; // Ensures the max value gets the last color.
    const index = Math.min(Math.floor((value - minValue) / segmentSize), colors.length - 2);
    return colors[index];
  };
};

