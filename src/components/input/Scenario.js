import React from "react";

import Box from "@mui/material/Box";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import InputLabel from "@mui/material/InputLabel";
import MenuItem from "@mui/material/MenuItem";
import OutlinedInput from "@mui/material/OutlinedInput";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import Select from "@mui/material/Select";
import Typography from "@mui/material/Typography";

const FUTURE_SCENARIOS = [
  { label: "RCP 2.6", value: "rcp26" },
  { label: "RCP 4.5d", value: "rcp45" },
  { label: "RCP 6.0", value: "rcp60" },
  { label: "RCP 8.5", value: "rcp85" },
];

const HISTORICAL_SCENARIOS = [{ label: "Historical", value: "historical" }];

const Scenario = (props) => {
  const scenariosToShow =
    props.scenarioCheck === "historical" ? HISTORICAL_SCENARIOS : FUTURE_SCENARIOS;

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
      <Typography id="scenario-dropdown" gutterBottom variant="h6" sx={{ fontWeight: "bold" }}>
        Scenario
      </Typography>

      <FormControl>
        <RadioGroup
          row
          aria-labelledby="timehorizon-radio-button-label"
          name="timehorizon-row-radio-buttons-group"
          onChange={props.onChangeRadio}
          defaultValue={"historical"}
          defaultChecked
        >
          <FormControlLabel
            value="historical"
            control={<Radio sx={{ "&.Mui-checked": { color: "#2A4D69" } }} />}
            label="Historical"
          />
          <FormControlLabel
            value="future"
            control={<Radio sx={{ "&.Mui-checked": { color: "#2A4D69" } }} />}
            label="Future projection"
          />
        </RadioGroup>
      </FormControl>
      <FormControl sx={{ m: 1, minWidth: 250, maxWidth: 300 }}>
        <InputLabel id="scenario-select-label">Scenario</InputLabel>
        <Select
          defaultValue=""
          disabled={props.disabled}
          id="scenario-select"
          input={<OutlinedInput label="Scenario" />}
          labelId="scenario-select-label"
          onChange={props.onChange}
          value={props.value}
        >
          {scenariosToShow.map((scenario) => (
            <MenuItem key={scenario.value} value={scenario.value}>
              {scenario.label}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  );
};

export default Scenario;
