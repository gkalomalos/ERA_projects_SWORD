import React from "react";

import Box from "@mui/material/Box";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import Typography from "@mui/material/Typography";

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
          <MenuItem disabled>Economical</MenuItem>
          <MenuItem key="litpop" value="litpop">
            LitPop
          </MenuItem>
          <MenuItem key="crop-production" value="crop-production">
            Crop production
          </MenuItem>
          <MenuItem disabled>Non-Economical</MenuItem>
          <MenuItem key="crops" value="crops">
            Crops
          </MenuItem>
          <MenuItem key="education" value="education">
            Education
          </MenuItem>
        </Select>
      </FormControl>
    </Box>
  );
};

export default ExposureType;
