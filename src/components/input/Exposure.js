import React from "react";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import Typography from "@mui/material/Typography";

const exposureTypeOptions = [
  { key: "economical-label", value: "", name: "Economical", isLabel: true },
  { key: "litpop", value: "litpop", name: "LitPop" },
  { key: "crop-production", value: "crop-production", name: "Crop production" },
  {
    key: "non-economical-label",
    value: "",
    name: "Non-Economical",
    isLabel: true,
  },
  { key: "crops", value: "crops", name: "Crops" },
  { key: "education", value: "education", name: "Education" },
];

const Exposure = (props) => {
  return (
    <Box sx={{ minWidth: 250, maxWidth: 250, margin: 4 }}>
      <Box sx={{ marginBottom: 2 }}>
        <Typography
          id="exposure-type-heading"
          gutterBottom
          variant="h6"
          sx={{ fontWeight: "bold" }}
        >
          Exposure
        </Typography>
      </Box>

      <Box sx={{ marginBottom: 2 }}>
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

      <Box sx={{ display: "flex", gap: 2 }}>
        <Button
          variant="contained"
          sx={{ bgcolor: "#2A4D69", "&:hover": { bgcolor: "5C87B1" } }}
          onClick={props.onFetchChange}
        >
          Fetch
        </Button>

        <label htmlFor="exposure-contained-button-file">
          <Button
            component="span"
            variant="contained"
            sx={{ bgcolor: "#2A4D69", "&:hover": { bgcolor: "5C87B1" } }}
          >
            Load
          </Button>
          <input
            accept=".xlsx"
            hidden
            id="exposure-contained-button-file"
            multiple={false}
            onChange={props.onLoadChange}
            type="file"
          />
        </label>
      </Box>
    </Box>
  );
};

export default Exposure;
