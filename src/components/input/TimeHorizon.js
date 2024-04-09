import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { Box, Card, CardContent, TextField, Typography } from "@mui/material";

const TimeHorizon = (props) => {
  const { t } = useTranslation();
  const [clicked, setClicked] = useState(false); // State to manage click animation
  const [bgColor, setBgColor] = useState("#EBF3F5"); // State to manage background color

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

  const handleClick = () => {
    // Deactivate input card click in case of ERA project scenario.
    // Time horizon is set to 2050
    if (props.selectedAppOption === "era") {
      return;
    }
    props.onCardClick("timeHorizon");
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
  }, [props.selectedAppOption, props.selectedCountry]);

  return (
    <Card
      variant="outlined"
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp} // Reset animation when the mouse leaves the card
      onClick={handleClick}
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
        <Box>
          <Typography id="time-horizon-dropdown" gutterBottom variant="h6" component="div" m={0}>
            {t("time_horizon_title")}
          </Typography>
          {props.selectedTimeHorizon && (
            <TextField
              id="timeHorizon"
              fullWidth
              variant="outlined"
              value={props.selectedTimeHorizon}
              disabled
              InputProps={{
                readOnly: true,
              }}
              sx={{
                ".MuiInputBase-input.Mui-disabled": {
                  WebkitTextFillColor: "#A6A6A6", // Change the text color for disabled content
                  bgcolor: "#E6E6E6", // Change background for disabled TextField
                  padding: 1,
                },
              }}
            />
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default TimeHorizon;
