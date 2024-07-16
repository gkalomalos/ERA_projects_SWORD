import { schemeReds, schemeBlues, schemeYlOrBr, schemeYlOrRd } from "d3-scale-chromatic";

const getColorScale = (hazard) => {
  const k = 9; // Largest set of colors
  switch (hazard) {
    case "flood":
      return schemeBlues[k].slice(-5); // Get last 5 colors
    case "drought":
      return [...schemeYlOrBr[k]].slice(-5).reverse();
    case "heatwaves":
      return schemeReds[k].slice(-5);
    default:
      return schemeYlOrRd[k].slice(-5);
  }
};

export const getScale = (hazard, percentileValues) => {
  const colors = getColorScale(hazard);
  // Ensure the percentileValues are sorted (important if values can be in any order)
  percentileValues.sort((a, b) => a - b);

  return (value) => {
    // Determine if values are in ascending or descending order
    const isAscending = percentileValues[0] < percentileValues[percentileValues.length - 1];

    if (isAscending) {
      for (let i = 0; i < percentileValues.length - 1; i++) {
        if (value >= percentileValues[i] && value < percentileValues[i + 1]) {
          return colors[i];
        }
      }
    } else {
      // Handle descending order values
      for (let i = percentileValues.length - 1; i > 0; i--) {
        if (value <= percentileValues[i] && value > percentileValues[i - 1]) {
          return colors[percentileValues.length - i - 1];
        }
      }
    }
    // Handle the edge case for the last segment
    return colors[isAscending ? colors.length - 1 : 0];
  };
};
