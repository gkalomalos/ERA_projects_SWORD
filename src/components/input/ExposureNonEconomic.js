import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";

import { Box, Card, CardContent, TextField, Typography } from "@mui/material";

const ExposureNonEconomic = (props) => {
  const { t } = useTranslation();
  const [clicked, setClicked] = useState(false); // State to manage click animation
  const [bgColor, setBgColor] = useState("#EBF3F5"); // State to manage background color

  const handleMouseDown = () => {
    if (props.selectedExposureEconomic) {
      return;
    }
    setClicked(true); // Trigger animation
  };

  const handleMouseUp = () => {
    if (props.selectedExposureEconomic) {
      return;
    }
    setClicked(false); // Reset animation
  };

  const handleClick = () => {
    if (props.selectedExposureEconomic) {
      return;
    }
    props.onCardClick("exposureNonEconomic");
    props.onSelectTab(0);
  };

  const handleBgColor = () => {
    if (props.selectedExposureNonEconomic && props.isValidExposureNonEconomic) {
      setBgColor("#E5F5EB"); //green
    } else if (props.selectedExposureNonEconomic && !props.isValidExposureNonEconomic) {
      setBgColor("#FFCCCC"); //red
    } else if (props.selectedExposureEconomic) {
      setBgColor("#E6E6E6"); //grey
    } else {
      setBgColor("#EBF3F5"); //default light blue
    }
  };

  useEffect(() => {
    handleBgColor();
  }, [
    props.isValidExposureNonEconomic,
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
            {t("input_exposure_non_economic_title")}
          </Typography>
          {props.selectedExposureNonEconomic && (
            <TextField
              id="exposure-non-economic-textfield"
              fullWidth
              variant="outlined"
              value={t(`input_exposure_non_economic_${props.selectedExposureNonEconomic}`)}
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

export default ExposureNonEconomic;
