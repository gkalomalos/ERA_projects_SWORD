import React, { useState } from "react";
import { useTranslation } from "react-i18next";

import { Box, Button, Typography } from "@mui/material";

import ResultsTypography from "./ResultsTypography";
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

        <ResultsTypography />
      </Box>
    </Box>
  );
};

export default EconomicResultsCard;
