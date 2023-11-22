import React from "react";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import CancelIcon from "@mui/icons-material/Cancel";
import Chip from "@mui/material/Chip";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import OutlinedInput from "@mui/material/OutlinedInput";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import Select from "@mui/material/Select";
import Typography from "@mui/material/Typography";

const COUNTRIES = ["Egypt"];
// const COUNTRIES = ["Egypt", "Thailand"];

const Exposure = (props) => {
  return (
    <Box sx={{ minWidth: 250, maxWidth: 350, margin: 4 }}>
      <Typography
        id="exposure-dropdown"
        gutterBottom
        variant="h6"
        sx={{ fontWeight: "bold" }}
      >
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
            value="load"
            control={<Radio sx={{ "&.Mui-checked": { color: "#2A4D69" } }} />}
            label="Load exposure"
          />
        </RadioGroup>
      </FormControl>
      {props.exposureCheck === "select" && (
        <FormControl sx={{ m: 1, minWidth: 250, maxWidth: 300 }}>
          <InputLabel id="exposure-select-label">Exposure</InputLabel>
          <Select
            id="exposure-select"
            input={<OutlinedInput label="Exposure" />}
            labelId="exposure-select-label"
            multiple
            onChange={props.onChangeSelect}
            value={props.value}
            disabled={props.value.length > 3}
            renderValue={(selected) => (
              <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
                {selected.map((value) => (
                  <Chip
                    clickable
                    deleteIcon={<CancelIcon />}
                    key={value}
                    label={value}
                    onDelete={(e) => props.chipDelete(e, value)}
                    onMouseDown={(event) => {
                      event.stopPropagation();
                    }}
                    color={props.value.length < 4 ? "default" : "error"}
                  />
                ))}
              </Box>
            )}
          >
            {COUNTRIES.map((country) => (
              <MenuItem key={country} value={country}>
                {country}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      )}
      {props.exposureCheck === "load" && (
        <label htmlFor="exposure-contained-button-file">
          <Button
            component="span"
            variant="contained"
            sx={{ bgcolor: "#2A4D69", "&:hover": { bgcolor: "5C87B1" } }}
          >
            Load
            <input
              accept=".xlsx"
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
