import React from "react";

import Box from "@mui/material/Box";
import Slider from "@mui/material/Slider";
import Typography from "@mui/material/Typography";

const ANNUAL_GROWTH = [
  { value: 0, label: "0" },
  { value: 2, label: "2.0" },
  { value: 4, label: "4.0" },
  { value: 6, label: "6.0" },
  { value: 8, label: "8.0" },
  { value: 10, label: "10.0" },
];

const AnnualGrowth = (props) => {
  return (
    <Box sx={{ minWidth: 250, maxWidth: 300, margin: 4 }}>
      <Typography
        id="annual-growth-slider"
        gutterBottom
        variant="h6"
        sx={{ fontWeight: "bold" }}
      >
        Annual Growth
      </Typography>
      <Slider
        defaultValue={0}
        marks={ANNUAL_GROWTH}
        max={10}
        min={0}
        onChange={props.onChange}
        size="medium"
        step={0.5}
        sx={{ color: "#2A4D69" }}
        valueLabelDisplay="auto"
      />
    </Box>
  );
};

export default AnnualGrowth;
