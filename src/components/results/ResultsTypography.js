import React from "react";
import { useTranslation } from "react-i18next";

import { Typography } from "@mui/material";

import useStore from "../../store";

const ResultsTypography = () => {
  const {
    activeMap,
    selectedAppOption,
    selectedCountry,
    selectedHazard,
    selectedExposureEconomic,
    selectedExposureNonEconomic,
    selectedTab,
    selectedSubTab,
    viewControl,
  } = useStore();
  const { t } = useTranslation();

  const getText = () => {
    if (
      !selectedAppOption ||
      !selectedCountry ||
      !selectedHazard ||
      (!selectedExposureEconomic && !selectedExposureNonEconomic)
    ) {
      return "";
    }

    const selectedExposure = selectedExposureEconomic || selectedExposureNonEconomic;

    return t(
      `results_${selectedAppOption}_` +
        `${selectedCountry}_` +
        `${selectedHazard}_` +
        `${selectedExposure}_` +
        `${selectedTab}_` +
        `${selectedSubTab}_` +
        `${viewControl}_` +
        `${activeMap}`
    );
  };

  return (
    <Typography variant="body1" sx={{ marginTop: 2, flexGrow: 1, color: "#6F6F6F" }}>
      {getText()}
    </Typography>
  );
};

export default ResultsTypography;
