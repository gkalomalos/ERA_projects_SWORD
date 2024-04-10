import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { Box, Card, CardContent, TextField, Typography } from "@mui/material";

const AnnualGrowth = (props) => {
  const { t } = useTranslation();
  const [clicked, setClicked] = useState(false); // State to manage click animation
  const [bgColor, setBgColor] = useState("#EBF3F5"); // State to manage background color
  const [gdpGrowth, setGdpGrowth] = useState(props.selectedAnnualGDPGrowth);
  const [populationGrowth, setPopulationGrowth] = useState(props.selectedAnnualPopulationGrowth);

  const handleMouseDown = () => {
    // Deactivate input card click in case of ERA project scenario.
    // Time horizon is set to 2050
    if (props.selectedAppOption === "era") {
      return;
    }
    setClicked(true); // Trigger animation
  };

  const handleMouseUp = () => {
    // Deactivate input card click in case of ERA project scenario.
    // Time horizon is set to 2050
    if (props.selectedAppOption === "era") {
      return;
    }
    setClicked(false); // Reset animation
  };

  const handleCardClick = () => {
    // Deactivate input card click in case of ERA project scenario.
    // Time horizon is set to 2050
    if (props.selectedAppOption === "era") {
      return;
    }
    props.onCardClick("annualGrowth");
    props.onSelectTab(0);
  };

  const handleBgColor = () => {
    if (props.selectedAppOption === "era" && props.selectedCountry) {
      setBgColor("#E5F5EB"); //green
      // } else if (props.selectedAppOption === "era") {
      //   setBgColor("#FFCCCC"); //red
      // } else if (props.selectedAppOption === "era") {
      //   setBgColor("#E6E6E6"); //grey
    } else {
      setBgColor("#EBF3F5"); //default light blue
    }
  };

  useEffect(() => {
    handleBgColor();
    if (props.selectedAppOption === "era") {
      if (props.selectedCountry === "thailand") {
        setGdpGrowth(2.94);
        setPopulationGrowth(-0.22);
      } else if (props.selectedCountry === "egypt") {
        setGdpGrowth(4);
        setPopulationGrowth(1.29);
      } else {
        // Reset to defaults or handle other countries as needed
        setGdpGrowth(props.selectedAnnualGDPGrowth);
        setPopulationGrowth(props.selectedAnnualPopulationGrowth);
      }
    } else {
      // If not "era", use the provided props values
      setGdpGrowth(props.selectedAnnualGDPGrowth);
      setPopulationGrowth(props.selectedAnnualPopulationGrowth);
    }
  }, [props.selectedAppOption, props.selectedCountry]);

  return (
    <Card
      variant="outlined"
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp} // Reset animation when the mouse leaves the card
      onClick={handleCardClick}
      sx={{
        cursor: "pointer",
        bgcolor: bgColor,
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
            value={`${gdpGrowth}%`}
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
            {t("input_annual_population_growth_title")}
          </Typography>
          <TextField
            id="annual-growth-population-textfield"
            fullWidth
            variant="outlined"
            value={`${populationGrowth}%`}
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
