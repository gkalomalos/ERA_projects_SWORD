import React from "react";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import OutlinedInput from "@mui/material/OutlinedInput";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import Select from "@mui/material/Select";
import Typography from "@mui/material/Typography";

const HAZARDS = [
  { key: "hydrological-label", value: "", name: "Hydrological", isLabel: true },
  { key: "river-flood", value: "river_flood", name: "River flood" },
  { key: "flood", value: "flood", name: "Flood" },
  { key: "geophysical-label", value: "", name: "Geophysical", isLabel: true },
  { key: "eartquake", value: "crops", name: "Crops" },
  { key: "meteorological-label", value: "", name: "Meteorological", isLabel: true },
  { key: "tropical-cyclone", value: "tropical_cyclone", name: "Tropical Cyclone" },
  { key: "climatological-label", value: "", name: "Climatological", isLabel: true },
  { key: "wildfire", value: "wildfire", name: "Wildfire" },
];

const Hazard = (props) => {
  return (
    <Box
      sx={{
        minWidth: 250,
        maxWidth: 350,
        marginBottom: 4,
        marginLeft: 4,
        marginTop: 4,
        marginRight: 0,
      }}
    >
      <Typography id="hazard-dropdown" gutterBottom sx={{ fontWeight: "bold" }} variant="h6">
        Hazard
      </Typography>
      <FormControl>
        <RadioGroup
          aria-labelledby="hazard-radio-button-label"
          defaultChecked
          defaultValue={props.defaultValue}
          name="hazard-row-radio-buttons-group"
          onChange={props.onChangeRadio}
          row
        >
          <FormControlLabel
            control={<Radio sx={{ "&.Mui-checked": { color: "#2A4D69" } }} />}
            label="Select hazard"
            value="select"
          />
          <FormControlLabel
            control={<Radio sx={{ "&.Mui-checked": { color: "#2A4D69" } }} />}
            label="Load hazard"
            value="load"
          />
        </RadioGroup>
      </FormControl>
      {props.hazardCheck === "select" && (
        <FormControl sx={{ m: 1, minWidth: 250, maxWidth: 300 }}>
          <InputLabel id="hazard-select-label">Hazard</InputLabel>
          <Select
            defaultValue=""
            disabled={props.disabled}
            id="hazard-select"
            input={<OutlinedInput label="Hazard" />}
            labelId="hazard-select-label"
            onChange={props.onSelectChange}
            value={props.value}
          >
            {HAZARDS.map((option) => (
              <MenuItem
                key={option.key}
                value={option.value}
                disabled={option.isLabel}
                style={{ paddingLeft: option.isLabel ? "20px" : "30px" }}
              >
                {option.name}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}
      {props.hazardCheck === "load" && (
        <label htmlFor="hazard-contained-button-file">
          <Button
            component="span"
            disabled={props.disabled}
            sx={{ bgcolor: "#2A4D69", "&:hover": { bgcolor: "5C87B1" } }}
            variant="contained"
          >
            Load
            <input
              accept=".hdf5"
              hidden
              id="hazard-contained-button-file"
              multiple={false}
              onChange={props.onLoadChange}
              type="file"
            />
          </Button>
        </label>
      )}
    </Box>
  );
};

export default Hazard;
