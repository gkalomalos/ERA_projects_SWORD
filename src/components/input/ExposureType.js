import React from 'react';
import Box from "@mui/material/Box";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import Typography from "@mui/material/Typography";

const EXPOSURE_TYPES = ["Litpop", "Buildings"];

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
          onChange={props.onSelectExposureTypeChange}
        >
          {EXPOSURE_TYPES.map((exposureType) => (
            <MenuItem key={exposureType} value={exposureType}>
              {exposureType}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  );
};

export default ExposureType;
