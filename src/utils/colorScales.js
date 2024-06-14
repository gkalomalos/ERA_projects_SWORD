import {
  interpolateRdYlGn,
  interpolateBlues,
  interpolateYlOrBr,
  interpolateReds,
} from "d3-scale-chromatic";
import { scaleSequential } from "d3-scale";

const interpolateRdYlGnReversed = (t) => interpolateRdYlGn(1 - t);
const interpolateBluesReversed = (t) => interpolateBlues(1 - t);
const interpolateRedsReversed = (t) => interpolateReds(1 - t);
// const interpolateYlOrBrReversed = (t) => interpolateYlOrBr(1 - t);

export const getColorScale = (hazard) => {
  switch (hazard) {
    case "flood":
      return interpolateBluesReversed;
    case "drought":
      return interpolateYlOrBr;
    case "heatwaves":
      return interpolateRedsReversed;
    default:
      return interpolateRdYlGnReversed;
  }
};

export const getScale = (hazard, maxValue, minValue) => {
  const colorScale = getColorScale(hazard);
  return scaleSequential(colorScale).domain([maxValue, minValue]);
};
