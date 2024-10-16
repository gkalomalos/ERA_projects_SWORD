import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { Box, Button } from "@mui/material";
import LoadingButton from "@mui/lab/LoadingButton";
import InsightsIcon from "@mui/icons-material/Insights";

import APIService from "../../APIService";
import useStore from "../../store";

const RunPlotMacroButton = () => {
  const { t } = useTranslation();
  const {
    selectedMacroCountry,
    selectedMacroHazard,
    selectedMacroScenario,
    selectedMacroSector,
    selectedMacroVariable,
    setAlertMessage,
    setAlertSeverity,
    setAlertShowMessage,
    setIsPlotMacroChartCompleted,
    setIsPlotMacroChartRunning,
    setMacroEconomicChartData,
    setMacroEconomicChartTitle,
  } = useStore();

  const [isPlotButtonLoading, setIsPlotButtonLoading] = useState(false);
  const [isPlotButtonDisabled, setIsPlotButtonDisabled] = useState(true);

  const isValid = () =>
    selectedMacroCountry &&
    selectedMacroHazard &&
    selectedMacroScenario &&
    selectedMacroSector &&
    selectedMacroVariable;

  useEffect(() => {
    setIsPlotButtonDisabled(!isValid());
  }, [
    selectedMacroCountry,
    selectedMacroHazard,
    selectedMacroScenario,
    selectedMacroSector,
    selectedMacroVariable,
  ]);

  const handleRunButton = () => {
    const body = {
      countryName: selectedMacroCountry,
      hazardType: selectedMacroHazard,
      scenario: selectedMacroScenario,
      sector: selectedMacroSector,
      variable: selectedMacroVariable,
    };

    setIsPlotButtonLoading(true);
    setIsPlotMacroChartRunning(true);

    APIService.FetchMacroEconomicChartData(body)
      .then((response) => {
        setAlertMessage(response.result.status.message);
        response.result.status.code === 2000
          ? setAlertSeverity("success")
          : setAlertSeverity("error");
        setMacroEconomicChartData(response.result.data);
        setMacroEconomicChartTitle(response.result.data.title);
        setAlertShowMessage(true);
        setIsPlotButtonLoading(false);
        setIsPlotMacroChartRunning(false);
        setIsPlotMacroChartCompleted(true);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  return (
    <Box sx={{ textAlign: "center", mt: 2 }}>
      {!isPlotButtonLoading ? (
        <Button
          key="runButton"
          disabled={isPlotButtonDisabled}
          onClick={handleRunButton}
          size="medium"
          startIcon={<InsightsIcon />}
          sx={{
            minWidth: "120px",
            bgcolor: "#F79191",
            "&:hover": { bgcolor: "#FFCCCC" },
          }}
          variant="contained"
        >
          {t("run_macro_plot_button")}
        </Button>
      ) : (
        <LoadingButton
          loading={isPlotButtonLoading}
          loadingPosition="center"
          sx={{ minWidth: "120px" }}
          color="secondary"
          variant="contained"
        >
          {t("run_plot_macro_loading_button")}
        </LoadingButton>
      )}
    </Box>
  );
};

export default RunPlotMacroButton;
