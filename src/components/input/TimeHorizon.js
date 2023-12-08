import React from "react";

import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import FormControl from "@mui/material/FormControl";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import OutlinedInput from "@mui/material/OutlinedInput";
import Select from "@mui/material/Select";

const FUTURE_TIME_HORIZON = [
  { label: "2010 - 2030", value: "2010_2030" },
  { label: "2030 - 2050", value: "2030_2050" },
  { label: "2050 - 2070", value: "2050_2070" },
  { label: "2070 - 2090", value: "2070_2090" },
];

const HISTORICAL_TIME_HORIZON = [{ label: "1980 - 2020", value: "1980_2020" }];

const TimeHorizon = (props) => {
  const timeHorizonsToShow =
    props.scenario === "historical" ? HISTORICAL_TIME_HORIZON : FUTURE_TIME_HORIZON;
  return (
    <Box sx={{ minWidth: 250, maxWidth: 350, margin: 4 }}>
      <Typography id="time-horizon-dropdown" gutterBottom variant="h6" sx={{ fontWeight: "bold" }}>
        Time Horizon
      </Typography>
      <FormControl sx={{ m: 1, minWidth: 250, maxWidth: 300 }}>
        <InputLabel id="scenario-select-label">Time Horizon</InputLabel>
        <Select
          defaultValue=""
          disabled={props.disabled}
          id="time-horizon-select"
          input={<OutlinedInput label="Time Horizon" />}
          labelId="time-horizon-select-label"
          onChange={props.onSelectChange}
          value={props.value}
        >
          {timeHorizonsToShow.map((horizon) => (
            <MenuItem key={horizon.value} value={horizon.value}>
              {horizon.label}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  );
};

export default TimeHorizon;
