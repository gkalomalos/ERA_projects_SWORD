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

const EXPOSURES = [
  { key: "economical-label", value: "", name: "Economical", isLabel: true },
  { key: "litpop", value: "litpop", name: "LitPop" },
  { key: "crop-production", value: "crop_production", name: "Crop production" },
  {
    key: "non-economical-label",
    value: "",
    name: "Non-Economical",
    isLabel: true,
  },
  { key: "crops", value: "crops", name: "Crops" },
];

const Exposure = (props) => {
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
      <Typography id="exposure-dropdown" gutterBottom sx={{ fontWeight: "bold" }} variant="h6">
        Exposure
      </Typography>
      <FormControl>
        <RadioGroup
          aria-labelledby="exposure-radio-button-label"
          defaultChecked
          defaultValue={props.defaultValue}
          name="exposure-row-radio-buttons-group"
          onChange={props.onChangeRadio}
          row
        >
          <FormControlLabel
            control={<Radio sx={{ "&.Mui-checked": { color: "#2A4D69" } }} />}
            label="Select exposure"
            value="select"
          />
          <FormControlLabel
            control={<Radio sx={{ "&.Mui-checked": { color: "#2A4D69" } }} />}
            label="Load exposure"
            value="load"
          />
        </RadioGroup>
      </FormControl>
      {props.exposureCheck === "select" && (
        <FormControl sx={{ m: 1, minWidth: 250, maxWidth: 300 }}>
          <InputLabel id="exposure-select-label">Exposure</InputLabel>
          <Select
            defaultValue=""
            disabled={props.disabled}
            id="exposure-select"
            input={<OutlinedInput label="Exposure" />}
            labelId="exposure-select-label"
            onChange={props.onSelectChange}
            value={props.value}
          >
            {EXPOSURES.map((option) => (
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
      {props.exposureCheck === "load" && (
        <label htmlFor="exposure-contained-button-file">
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
              id="exposure-contained-button-file"
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

export default Exposure;
