import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";

import { Box, Card, CardContent, TextField, Typography } from "@mui/material";

const Scenario = (props) => {
  const { t } = useTranslation();
  const [clicked, setClicked] = useState(false); // State to manage click animation
  const [bgcolor, setBgcolor] = useState("#EBF3F5"); // State to manage background color

  const handleMouseDown = () => {
    setClicked(true); // Trigger animation
  };

  const handleMouseUp = () => {
    setClicked(false); // Reset animation
  };

  const handleClick = () => {
    props.onCardClick("scenario");
    props.onSelectTab(0);
  };

  const handleBgColor = () => {
    if (props.selectedScenario) {
      setBgcolor("#EBF3F5"); //change to #E5F5EB
    } else {
      setBgcolor("#EBF3F5") // Change to FFCCCC
    }
  };

  useEffect(() => {
    handleBgColor();
  }, [props.selectedScenario]);

  return (
    <Card
      variant="outlined"
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp} // Reset animation when the mouse leaves the card
      onClick={handleClick}
      sx={{
        cursor: "pointer",
        bgcolor: bgcolor,
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
          <Typography id="scenario-dropdown" gutterBottom variant="h6" component="div" m={0}>
            {t("scenario_title")}
          </Typography>

          {props.selectedScenario && (
            <TextField
              id="scenario"
              fullWidth
              variant="outlined"
              value={t(`input_scenario_scenarios_${props.selectedScenario}`)}
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

export default Scenario;
