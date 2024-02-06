import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";

import { Box, Card, CardContent, TextField, Typography } from "@mui/material";

const ExposureEconomic = (props) => {
  const { t } = useTranslation();
  const [clicked, setClicked] = useState(false); // State to manage click animation
  const [bgColor, setBgColor] = useState("#EBF3F5"); // State to manage background color

  const handleMouseDown = () => {
    if (props.selectedExposureNonEconomic) {
      return;
    }
    setClicked(true); // Trigger animation
  };

  const handleMouseUp = () => {
    if (props.selectedExposureNonEconomic) {
      return;
    }
    setClicked(false); // Reset animation
  };

  const handleClick = () => {
    if (props.selectedExposureNonEconomic) {
      return;
    }
    props.onCardClick("exposureEconomic");
    props.onSelectTab(0);
  };

  const handleBgColor = () => {
    if (props.selectedExposureEconomic && props.isValidExposureEconomic) {
      setBgColor("#E5F5EB"); //green
    } else if (props.selectedExposureEconomic && !props.isValidExposureEconomic) {
      setBgColor("#FFCCCC"); //red
    } else if (props.selectedExposureNonEconomic) {
      setBgColor("#E6E6E6"); //grey
    } else {
      setBgColor("#EBF3F5"); //default light blue
    }
  };

  // TODO:
  // 1. Define the Function Inside useEffect
  // If handleBgColor is only used in this useEffect and doesn't depend on external variables that
  // change over time, you could define it inside the useEffect itself. This way, it doesn't need to
  // be included in the dependency array:
  // 2. Use useCallback
  // If handleBgColor is used outside the useEffect or depends on props or state, you could wrap it
  // with useCallback to ensure it only gets redefined when its own dependencies change.
  // This makes it safe to include in the useEffect dependency array:
  // 3. Exclude the Function with a Justification
  // eslint-disable-next-line react-hooks/exhaustive-deps

  useEffect(() => {
    handleBgColor();
  }, [
    props.isValidExposureEconomic,
    props.selectedExposureEconomic,
    props.selectedExposureNonEconomic,
  ]);

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
          <Typography id="exposure-dropdown" gutterBottom variant="h6" component="div">
            {t("input_exposure_economic_title")}
          </Typography>
          {props.selectedExposureEconomic && (
            <TextField
              id="exposure-economic-textfield"
              fullWidth
              variant="outlined"
              value={t(`input_exposure_economic_${props.selectedExposureEconomic}`)}
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

export default ExposureEconomic;
