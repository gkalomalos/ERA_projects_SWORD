import React from "react";

import Box from "@mui/material/Box";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import Typography from "@mui/material/Typography";

const exposureTypeOptions = [
  { key: "economical-label", value: "", name: "Economical", isLabel: true },
  { key: "litpop", value: "litpop", name: "LitPop" },
  { key: "crop-production", value: "crop-production", name: "Crop production" },
  { key: "non-economical-label", value: "", name: "Non-Economical", isLabel: true },
  { key: "crops", value: "crops", name: "Crops" },
  { key: "education", value: "education", name: "Education" }
];


const ExposureType = (props) => {
  return (
    <Box sx={{ minWidth: 250, maxWidth: 250, margin: 4 }}>
      <Typography
        id="exposure-type-dropdown"
        gutterBottom
        variant="h6"
        sx={{ fontWeight: "bold" }}
      >
        Exposure Type
      </Typography>
      <FormControl fullWidth>
        <InputLabel id="exposure-type-select-label">Exposure Type</InputLabel>
        <Select
          labelId="exposure-type-select-label"
          id="exposure-type-select"
          value={props.selectedExposureType}
          label="Exposure Type"
          onChange={props.onExposureTypeChange}
        >
          {exposureTypeOptions.map((option) => (
            <MenuItem key={option.key} value={option.value} disabled={option.isLabel}>
              {option.name}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  );
};

export default ExposureType;
