import React from "react";
import { useTranslation } from "react-i18next";

import { Box, Button, Typography } from "@mui/material";

const OutputResultsCard = () => {
  const { t } = useTranslation();

  const handleButtonClick = (type) => {
    console.log(type);
  };

  return (
    <>
      <Box sx={{ display: "flex", flexDirection: "column", height: "100%" }}>
        {/* Button Section container for both sets of buttons */}
        <Box sx={{ display: "flex", justifyContent: "space-around" }}>
          {/* First set of buttons container */}
          <Box sx={{ display: "flex", flexDirection: "column" }}>
            {["pdf", "word"].map((type) => (
              <Button
                key={type}
                variant="contained"
                size="small"
                sx={{
                  marginBottom: 2,
                  bgcolor: "#FFCCCC",
                  transition: "transform 0.1s ease-in-out",
                  "&:active": {
                    transform: "scale(0.96)",
                  },
                  "&:hover": { bgcolor: "#F79191" },
                  textTransform: "none",
                }}
                onClick={() => handleButtonClick(type)}
              >
                {t(`results_export_button_${type}`)}
              </Button>
            ))}
          </Box>

          {/* Second set of buttons container */}
          <Box sx={{ display: "flex", flexDirection: "column" }}>
            {["excel", "gis"].map((type) => (
              <Button
                key={type}
                variant="contained"
                size="small"
                sx={{
                  marginBottom: 2,
                  bgcolor: "#FFCCCC",
                  transition: "transform 0.1s ease-in-out",
                  "&:active": {
                    transform: "scale(0.96)",
                  },
                  "&:hover": { bgcolor: "#F79191" },
                  textTransform: "none",
                }}
                onClick={() => handleButtonClick(type)}
              >
                {t(`results_export_button_${type}`)}
              </Button>
            ))}
          </Box>
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
            {t("results_report_details")}
          </Typography>
          {/* Content here will grow to fill available space */}
          <Typography variant="body1" sx={{ marginTop: 2, flexGrow: 1, color: "#6F6F6F" }}>
            Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor
            incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud
            exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure
            dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
            Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt
            mollit anim id est laborum.
          </Typography>
        </Box>
      </Box>
    </>
  );
};

export default OutputResultsCard;
