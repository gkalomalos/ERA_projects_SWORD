import React from "react";
import { useTranslation } from "react-i18next";

import Box from "@mui/material/Box";
import FormControl from "@mui/material/FormControl";
import FormControlLabel from "@mui/material/FormControlLabel";
import Radio from "@mui/material/Radio";
import RadioGroup from "@mui/material/RadioGroup";
import Typography from "@mui/material/Typography";

const COUNTRIES = ["Egypt", "Thailand"];

const Country = (props) => {
  const { t } = useTranslation();

  return (
    <Box sx={{ minWidth: 250, maxWidth: 250, margin: 4 }}>
      <Typography
        id="country-radio-group-label"
        gutterBottom
        variant="h6"
        sx={{ fontWeight: "bold" }}
      >
        {t("country")}
      </Typography>
      <FormControl component="fieldset">
        <RadioGroup
          aria-labelledby="country-radio-group-label"
          name="country-radio-buttons-group"
          value={props.selectedCountry}
          onChange={props.onCountryChange}
          row
        >
          {COUNTRIES.map((country) => (
            <FormControlLabel
              key={country}
              value={country}
              control={<Radio sx={{ "&.Mui-checked": { color: "#2A4D69" } }} />}
              label={t(country)}
            />
          ))}
        </RadioGroup>
      </FormControl>
    </Box>
  );
};

export default Country;
