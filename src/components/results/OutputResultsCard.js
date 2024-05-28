import React from "react";
import { useTranslation } from "react-i18next";

import { Box, Button } from "@mui/material";

const OutputResultsCard = () => {
  const { t } = useTranslation();
  const handleButtonClick = (type) => {
    console.log(type);
  };

  return (
    <>
      <Box sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
        <Box sx={{ display: "flex", justifyContent: "space-around", marginBottom: 2 }}>
          <Box sx={{ display: "flex", flexDirection: "column", marginBottom: 2 }}>
            {["pdf", "excel", "word", "gis"].map((type) => (
              <Button
                key={type}
                variant="contained"
                sx={{
                  marginBottom: 2,
                  bgcolor: "#FFCCCC",
                  transition: "transform 0.1s ease-in-out",
                  "&:active": {
                    transform: "scale(0.96)",
                  },
                  "&:hover": { bgcolor: "#F79191" },
                }}
                onClick={() => handleButtonClick(type)}
              >
                {t(`results_export_button_${type}`)}
              </Button>
            ))}
          </Box>
          <Box sx={{ display: "flex", flexDirection: "column", marginBottom: 2 }}>
            {["gis", "ppt", "other"].map((type) => (
              <Button
                key={type}
                variant="contained"
                sx={{
                  marginBottom: 2,
                  bgcolor: "#FFCCCC",
                  transition: "transform 0.1s ease-in-out",
                  "&:active": {
                    transform: "scale(0.96)",
                  },
                  "&:hover": { bgcolor: "#F79191" },
                }}
                onClick={() => handleButtonClick(type)}
              >
                {t(`results_export_button_${type}`)}
              </Button>
            ))}
          </Box>
        </Box>
      </Box>
    </>
  );
};

export default OutputResultsCard;
