import React from "react";

import { useTranslation } from "react-i18next";
import { Box, Card, CardContent, Slider, Typography } from "@mui/material";

const populationMarks = [
  { value: -2, label: "-2%" },
  { value: 4, label: "4%" },
];
const gdpMarks = [
  { value: 0, label: "0%" },
  { value: 6, label: "6%" },
];

const gdpValueText = (value) => {
  return `${value}`;
};

const populationValueText = (value) => {
  return `${value}`;
};

const AnnualGrowthCard = ({
  onGDPSelect,
  onPopulationSelect,
  selectedAnnualGDPGrowth,
  selectedAnnualPopulationGrowth,
}) => {
  const { t } = useTranslation();

  const handleGDPCardSelect = (event, value) => {
    onGDPSelect(value);
  };
  const handlePopulationCardSelect = (event, value) => {
    onPopulationSelect(value);
  };

  return (
    <Card
      sx={{
        maxWidth: 800,
        margin: "auto",
        bgcolor: "#DCEFF2",
        border: "2px solid #3B919D",
        borderRadius: "16px",
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
            marginBottom: "16px",
          }}
        >
          {t("card_annualgrowth_title")}
        </Typography>
        <Box
          sx={{
            display: "flex",
            flexDirection: "row",
            justifyContent: "space-between", // Add space between the child components
            alignItems: "center",
            padding: "20px 0",
          }}
        >
          {/* GDP Box */}
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "center", // Center children horizontally
              backgroundColor: "#FFCCCC",
              borderRadius: "8px",
              padding: "20px 0",
              marginBottom: "16px",
              width: "50%", // Take up half of the parent container
              paddingRight: "16px",
              marginRight: "16px",
            }}
          >
            <Typography
              id="gdp-slider"
              gutterBottom
              variant="body1"
              component="div"
              textAlign="center"
              color="text.primary"
            >
              {t("card_annualgrowth_gdp_subtitle")}
            </Typography>
            <Slider
              aria-label="GDP selector"
              defaultValue={0}
              getAriaValueText={gdpValueText}
              onChange={handleGDPCardSelect} // Updated to the handleSelect function
              step={0.1}
              marks={gdpMarks}
              min={gdpMarks[0].value}
              max={gdpMarks[1].value}
              valueLabelDisplay="on" // Changed to "on" to always show the value label
              value={selectedAnnualGDPGrowth ? parseFloat(selectedAnnualGDPGrowth) : 0}
              sx={{
                color: "#F79191", // Slider track and thumb color
                marginTop: "48px ",
                width: "90%", // Adjust width to be less than container to center properly
                "& .MuiSlider-thumb": {
                  height: 24,
                  width: 24,
                  backgroundColor: "#fff",
                  border: "2px solid currentColor",
                  "&:focus, &:hover, &.Mui-active": {
                    boxShadow: "inherit",
                  },
                },
                "& .MuiSlider-valueLabel": {
                  color: "black",
                  variant: "body2",
                  fontWeight: "bold",
                  borderRadius: "16px",
                  borderColor: "black",
                  backgroundColor: "#F79191",
                },
                "& .MuiSlider-track": {
                  height: 16,
                  borderRadius: 4,
                },
                "& .MuiSlider-rail": {
                  color: "#d8d8d8",
                  opacity: 1,
                  height: 8,
                  borderRadius: 4,
                },
              }}
            />
          </Box>
          {/* Population Box */}
          <Box
            sx={{
              display: "flex",
              flexDirection: "column",
              justifyContent: "center",
              alignItems: "center", // Center children horizontally
              backgroundColor: "#FFCCCC",
              borderRadius: "8px",
              padding: "20px 0",
              marginBottom: "16px",
              width: "50%", // Take up half of the parent container
              paddingLeft: "16px",
              marginLeft: "16px",
            }}
          >
            <Typography
              id="population-slider"
              gutterBottom
              variant="body1"
              component="div"
              textAlign="center"
              color="text.primary"
            >
              {t("card_annualgrowth_population_subtitle")}
            </Typography>
            <Slider
              aria-label="Population selector"
              defaultValue={0}
              getAriaValueText={populationValueText}
              onChange={handlePopulationCardSelect} // Updated to the handleSelect function
              step={0.1}
              marks={populationMarks}
              min={populationMarks[0].value}
              max={populationMarks[1].value}
              valueLabelDisplay="on" // Changed to "on" to always show the value label
              value={
                selectedAnnualPopulationGrowth ? parseFloat(selectedAnnualPopulationGrowth) : 0
              }
              sx={{
                color: "#F79191", // Slider track and thumb color
                marginTop: "48px ",
                width: "90%", // Adjust width to be less than container to center properly
                "& .MuiSlider-thumb": {
                  height: 24,
                  width: 24,
                  backgroundColor: "#fff",
                  border: "2px solid currentColor",
                  "&:focus, &:hover, &.Mui-active": {
                    boxShadow: "inherit",
                  },
                },
                "& .MuiSlider-valueLabel": {
                  color: "black",
                  variant: "body2",
                  fontWeight: "bold",
                  borderRadius: "16px",
                  borderColor: "black",
                  backgroundColor: "#F79191",
                },
                "& .MuiSlider-track": {
                  height: 16,
                  borderRadius: 4,
                },
                "& .MuiSlider-rail": {
                  color: "#d8d8d8",
                  opacity: 1,
                  height: 8,
                  borderRadius: 4,
                },
              }}
            />
          </Box>
        </Box>
        <Box sx={{ padding: 2, backgroundColor: "#F2F2F2", borderRadius: "8px" }}>
          <Typography variant="body2" color="text.primary">
            {t("card_annualgrowth_remarks")}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default AnnualGrowthCard;
