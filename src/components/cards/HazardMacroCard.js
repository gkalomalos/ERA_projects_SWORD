import React from "react";
import { useTranslation } from "react-i18next";

import { Box, Card, CardActionArea, CardContent, Typography } from "@mui/material";

import useStore from "../../store";

const hazardDict = {
  thailand: ["flood", "drought", "heatwaves"],
  egypt: ["flood", "heatwaves"],
};

const HazardMacroCard = () => {
  const { t } = useTranslation();
  const { selectedCountry, selectedHazard, setSelectedHazard } = useStore();

  const hazards = hazardDict[selectedCountry] || [];

  const handleCardSelect = (hazard) => {
    if (selectedHazard === hazard) {
      setSelectedHazard("");
    } else {
      setSelectedHazard(hazard);
    }
  };

  const isButtonSelected = (hazard) => selectedHazard === hazard;

  return (
    <Card
      sx={{
        maxWidth: 800,
        margin: "auto",
        bgcolor: "#DCEFF2",
        border: "2px solid #3B919D",
        borderRadius: "16px",
        marginBottom: "16px",
      }}
    >
      <CardContent>
        <Typography
          gutterBottom
          variant="h5"
          component="div"
          color="text.primary"
          sx={{
            textAlign: "center",
            fontWeight: "bold",
            backgroundColor: "#F79191",
            borderRadius: "8px",
            padding: "8px",
            marginBottom: "24px",
          }}
        >
          {t("card_macro_hazard_title")}
        </Typography>

        {/* Hazard selection section */}
        <Box sx={{ display: "flex", flexDirection: "row", justifyContent: "center" }}>
          {hazards.map((hazard) => (
            <CardActionArea
              key={hazard}
              onClick={() => handleCardSelect(hazard)}
              sx={{
                backgroundColor: isButtonSelected(hazard) ? "#F79191" : "#FFCCCC",
                borderRadius: "8px",
                margin: "16px",
                marginLeft: 0,
                textAlign: "center",
                padding: "8px 0",
                transition: "transform 0.1s ease-in-out", // Add transition for transform
                "&:active": {
                  transform: "scale(0.96)", // Slightly scale down when clicked
                },
              }}
            >
              <Typography variant="body1" color="text.primary">
                {t(`card_hazard_${hazard}`)}
              </Typography>
            </CardActionArea>
          ))}
        </Box>

        {/* Remarks section */}
        <Box sx={{ padding: 2, backgroundColor: "#F2F2F2", borderRadius: "8px" }}>
          <Typography variant="body2" color="text.primary">
            {t("card_hazard_remarks")}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default HazardMacroCard;
