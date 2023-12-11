import React from "react";
import { useTranslation } from "react-i18next";

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
  { label: "rcp26_label", value: "rcp26" },
  { label: "rcp45_label", value: "rcp45" },
  { label: "rcp60_label", value: "rcp60" },
  { label: "rcp85_label", value: "rcp85" },
];

const HISTORICAL_SCENARIOS = [{ label: "historical_scenario_label", value: "historical" }];

const Scenario = (props) => {
  const { t } = useTranslation();
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
        {t("scenario_title")}
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
            label={t("historical_label")}
          />
          <FormControlLabel
            value="future"
            control={<Radio sx={{ "&.Mui-checked": { color: "#2A4D69" } }} />}
            label={t("future_projection_label")}
          />
        </RadioGroup>
      </FormControl>
      <FormControl sx={{ m: 1, minWidth: 250, maxWidth: 300 }}>
        <InputLabel id="scenario-select-label">{t("scenario_title")}</InputLabel>
        <Select
          defaultValue=""
          disabled={props.disabled}
          id="scenario-select"
          input={<OutlinedInput label={t("scenario_title")} />}
          labelId="scenario-select-label"
          onChange={props.onChange}
          value={props.value}
        >
          {scenariosToShow.map((scenario) => (
            <MenuItem key={scenario.value} value={scenario.value}>
              {t(scenario.label)}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
    </Box>
  );
};

export default Scenario;
