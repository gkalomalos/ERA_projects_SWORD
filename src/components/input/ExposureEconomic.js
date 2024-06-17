import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { Box, Card, CardContent, TextField, Typography } from "@mui/material";
import useStore from "../../store";

const ExposureEconomic = () => {
  const {
    isValidExposureEconomic,
    setSelectedCard,
    setSelectedTab,
    selectedExposureEconomic,
    selectedExposureNonEconomic,
  } = useStore();
  const { t } = useTranslation();
  const [clicked, setClicked] = useState(false); // State to manage click animation
  const [bgColor, setBgColor] = useState("#EBF3F5"); // State to manage background color

  const handleMouseDown = () => {
    // Deactivate input card click in case non-economic exposure is selected
    if (selectedExposureNonEconomic) {
      return;
    }
    setClicked(true); // Trigger animation
  };

  const handleMouseUp = () => {
    // Deactivate input card click in case non-economic exposure is selected
    if (selectedExposureNonEconomic) {
      return;
    }
    setClicked(false); // Reset animation
  };

  const handleClick = () => {
    if (selectedExposureNonEconomic) {
      return;
    }
    setSelectedCard("exposureEconomic");
    setSelectedTab(0);
  };

  const handleBgColor = () => {
    if (selectedExposureEconomic && isValidExposureEconomic) {
      setBgColor("#E5F5EB"); //green
    } else if (selectedExposureEconomic && !isValidExposureEconomic) {
      setBgColor("#FFCCCC"); //red
    } else if (selectedExposureNonEconomic) {
      setBgColor("#E6E6E6"); //grey
    } else {
      setBgColor("#EBF3F5"); //default light blue
    }
  };

  useEffect(() => {
    handleBgColor();
  }, [isValidExposureEconomic, selectedExposureEconomic, selectedExposureNonEconomic]);

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
          <Typography id="exposure-dropdown" gutterBottom variant="h6" component="div" m={0}>
            {t("input_exposure_economic_title")}
          </Typography>
          {selectedExposureEconomic && (
            <TextField
              id="exposure-economic-textfield"
              fullWidth
              variant="outlined"
              value={t(`input_exposure_economic_${selectedExposureEconomic}`)}
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
