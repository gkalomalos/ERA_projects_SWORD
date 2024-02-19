import React, { useState } from "react";
import { useTranslation } from "react-i18next";

import { Box, Card, CardContent, TextField, Typography } from "@mui/material";

const AnnualGrowth = (props) => {
  const { t } = useTranslation();
  const [clicked, setClicked] = useState(false); // State to manage click animation

  const handleMouseDown = () => {
    setClicked(true); // Trigger animation
  };

  const handleMouseUp = () => {
    setClicked(false); // Reset animation
  };

  const handleCardClick = () => {
    props.onCardClick("annualGrowth");
    props.onSelectTab(0);
  };

  return (
    <Card
      variant="outlined"
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp} // Reset animation when the mouse leaves the card
      onClick={handleCardClick}
      sx={{
        cursor: "pointer",
        bgcolor: "#EBF3F5",
        transition: "background-color 0.3s, transform 0.1s", // Added transform to the transition
        "&:hover": {
          bgcolor: "#DAE7EA",
        },
        ".MuiCardContent-root:last-child": {
          padding: 2,
        },
        transform: clicked ? "scale(0.97)" : "scale(1)", // Apply scale transform when clicked
      }}
    >
      <CardContent>
        {/* Annual GDP growth section */}
        <Box>
          <Typography id="annual-growth-gdp-slider" gutterBottom variant="h6" component="div" m={0}>
            {props.selectedAnnualGDPGrowth
              ? t("input_annual_gdp_growth_title")
              : t("input_annual_growth_title")}
          </Typography>
          <TextField
            id="annual-growth-gdp-textfield"
            fullWidth
            variant="outlined"
            value={`${props.selectedAnnualGDPGrowth}%`}
            disabled
            InputProps={{
              readOnly: true,
            }}
            sx={{
              ".MuiInputBase-input.Mui-disabled": {
                WebkitTextFillColor: "#A6A6A6", // Text color for disabled content
                bgcolor: "#E6E6E6", // Background for disabled TextField
                padding: 1,
              },
            }}
          />

          {/* Annual Population growth section */}
          <Typography
            id="annual-growth-population-slider"
            gutterBottom
            variant="h6"
            component="div"
          >
            {props.selectedAnnualPopulationGrowth ? t("input_annual_population_growth_title") : ""}
          </Typography>
          <TextField
            id="annual-growth-population-textfield"
            fullWidth
            variant="outlined"
            value={`${props.selectedAnnualPopulationGrowth}%`}
            disabled
            InputProps={{
              readOnly: true,
            }}
            sx={{
              ".MuiInputBase-input.Mui-disabled": {
                WebkitTextFillColor: "#A6A6A6", // Text color for disabled content
                bgcolor: "#E6E6E6", // Background for disabled TextField
                padding: 1,
              },
            }}
          />
        </Box>
      </CardContent>
    </Card>
  );
};

export default AnnualGrowth;
