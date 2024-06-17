import React, { useState } from "react";
import { useTranslation } from "react-i18next";

import { Box, Button, Typography } from "@mui/material";

import useStore from "../../store";

const EconomicResultsCard = () => {
  const { setActiveMap } = useStore();
  const { t } = useTranslation();
  const [selectedButton, setSelectedButton] = useState("hazard");

  const handleButtonClick = (type) => {
    setSelectedButton(type);
    setActiveMap(type);
  };

  const isButtonSelected = (type) => selectedButton === type;

  return (
    <Box sx={{ display: "flex", flexDirection: "column", height: "85vh" }}>
      {/* Button Section with flex column direction */}
      <Box sx={{ display: "flex", flexDirection: "column", marginBottom: 2 }}>
        {["hazard", "exposure", "impact"].map((type) => (
          <Button
            key={type}
            variant="contained"
            sx={{
              marginBottom: 2,
              bgcolor: isButtonSelected(type) ? "#F79191" : "#FFCCCC",
              transition: "transform 0.1s ease-in-out",
              "&:active": {
                transform: "scale(0.96)",
              },
              "&:hover": { bgcolor: "#F79191" },
            }}
            onClick={() => handleButtonClick(type)}
          >
            {t(`results_eco_button_${type}`)}
          </Button>
        ))}
      </Box>
      {/* Result Details section */}
      <Box
        sx={{
          bgcolor: "#FFCCCC",
          padding: 2,
          borderRadius: "4px",
        }}
      >
        <Typography
          variant="h6"
          sx={{
            borderBottom: "1px solid #6F6F6F",
            paddingBottom: 1,
            color: "#6F6F6F",
            textAlign: "center",
          }}
        >
          {t("results_eco_details")}
        </Typography>
        {/* Content here will grow to fill available space */}
        <Typography variant="body1" sx={{ marginTop: 2, flexGrow: 1, color: "#6F6F6F" }}>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt
          ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation
          ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in
          reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur
          sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id
          est laborum.
        </Typography>
      </Box>
    </Box>
  );
};

export default EconomicResultsCard;
