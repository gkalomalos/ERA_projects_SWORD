import React, { useState, useEffect } from "react";
import { useTranslation } from "react-i18next";

import { Box, Button, Grid } from "@mui/material";
import LoadingButton from "@mui/lab/LoadingButton";
import PlayCircleIcon from "@mui/icons-material/PlayCircle";

import AnnualGrowth from "./AnnualGrowth";
import APIService from "../../APIService";
import Country from "./Country";
import DataInputViewTitle from "../title/DataInputViewTitle";
import ExposureEconomic from "./ExposureEconomic";
import ExposureNonEconomic from "./ExposureNonEconomic";
import Hazard from "./Hazard";
import Scenario from "./Scenario";
import TimeHorizon from "./TimeHorizon";
import useStore from "../../store";

import AlertMessage from "../alerts/AlertMessage";

const DataInput = () => {
  const {
    isValidExposureEconomic,
    isValidExposureNonEconomic,
    isValidHazard,
    setSelectedCard,
    setMapTitle,
    setIsScenarioRunning,
    setSelectedTab,
    selectedCountry,
    selectedAnnualGrowth,
    selectedAppOption,
    selectedExposureEconomic,
    selectedExposureFile,
    selectedExposureNonEconomic,
    selectedHazard,
    selectedHazardFile,
    selectedScenario,
    selectedTimeHorizon,
  } = useStore();
  const { t } = useTranslation();

  const [isRunButtonLoading, setIsRunButtonLoading] = useState(false);
  const [isRunButtonDisabled, setIsRunButtonDisabled] = useState(true);
  const [message, setMessage] = useState("");
  const [severity, setSeverity] = useState("info");
  const [showMessage, setShowMessage] = useState(true);

  const onRunHandler = () => {
    const body = {
      annualGrowth: selectedAnnualGrowth,
      countryName: selectedCountry,
      exposureEconomic: selectedExposureEconomic,
      exposureFile: selectedExposureFile,
      exposureNonEconomic: selectedExposureNonEconomic,
      hazardType: selectedHazard,
      isEra: selectedAppOption === "era" ? true : false,
      hazardFile: selectedHazardFile,
      scenario: selectedScenario,
      timeHorizon: selectedTimeHorizon,
    };
    setIsRunButtonDisabled(true);
    setIsRunButtonLoading(true);
    setIsScenarioRunning(true);
    APIService.Run(body)
      .then((response) => {
        setMessage(response.result.status.message);
        response.result.status.code === 2000 ? setSeverity("success") : setSeverity("error");
        setShowMessage(true);
        setIsRunButtonLoading(false);
        setIsRunButtonDisabled(false);
        setMapTitle(response.result.data.mapTitle);
        setIsScenarioRunning(false);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  const handleCloseMessage = () => {
    setShowMessage(false);
  };

  const onCardClickHandler = (card) => {
    setSelectedCard(card);
  };

  const handleRunButton = () => {
    if (
      selectedCountry &&
      selectedHazard &&
      selectedScenario &&
      (selectedExposureEconomic || selectedExposureNonEconomic) &&
      isValidHazard &&
      (isValidExposureEconomic || isValidExposureNonEconomic)
    ) {
      setIsRunButtonDisabled(false);
    } else {
      setIsRunButtonDisabled(true);
    }
  };

  useEffect(() => {
    handleRunButton();
  }, [
    selectedCountry,
    selectedAnnualGrowth,
    selectedAppOption,
    selectedExposureEconomic,
    selectedExposureFile,
    selectedExposureNonEconomic,
    selectedHazard,
    selectedHazardFile,
    selectedScenario,
    selectedTimeHorizon,
  ]);

  return (
    <>
      {/* DataInput title section */}
      <DataInputViewTitle />

      {/* DataInput parameters section */}
      <Box sx={{ backgroundColor: "#DDEBEF", padding: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Country
              onCardClick={onCardClickHandler}
              onSelectTab={setSelectedTab}
              selectedCountry={selectedCountry}
            />
          </Grid>
          <Grid item xs={12}>
            <Hazard
              isValidHazard={isValidHazard}
              onCardClick={onCardClickHandler}
              onSelectTab={setSelectedTab}
              selectedHazard={selectedHazard}
            />
          </Grid>
          <Grid item xs={12}>
            <Scenario
              onCardClick={onCardClickHandler}
              onSelectTab={setSelectedTab}
              selectedScenario={selectedScenario}
            />
          </Grid>
          <Grid item xs={12}>
            <TimeHorizon
              onCardClick={onCardClickHandler}
              onSelectTab={setSelectedTab}
              selectedAppOption={selectedAppOption}
              selectedCountry={selectedCountry}
              selectedTimeHorizon={selectedTimeHorizon}
            />
          </Grid>
          <Grid item xs={12}>
            <ExposureEconomic
              isValidExposureEconomic={isValidExposureEconomic}
              onCardClick={onCardClickHandler}
              onSelectTab={setSelectedTab}
              selectedExposureEconomic={selectedExposureEconomic}
              selectedExposureNonEconomic={selectedExposureNonEconomic}
            />
          </Grid>
          <Grid item xs={12}>
            <ExposureNonEconomic
              isValidExposureNonEconomic={isValidExposureNonEconomic}
              onCardClick={onCardClickHandler}
              onSelectTab={setSelectedTab}
              selectedExposureEconomic={selectedExposureEconomic}
              selectedExposureNonEconomic={selectedExposureNonEconomic}
            />
          </Grid>
          <Grid item xs={12}>
            <AnnualGrowth
              onCardClick={onCardClickHandler}
              onSelectTab={setSelectedTab}
              selectedAnnualGrowth={selectedAnnualGrowth}
              selectedAppOption={selectedAppOption}
              selectedCountry={selectedCountry}
              selectedExposureEconomic={selectedExposureEconomic}
              selectedExposureNonEconomic={selectedExposureNonEconomic}
            />
          </Grid>
        </Grid>

        {/* Run button section */}
        <Grid item xs={12}>
          <Box sx={{ textAlign: "center", mt: 2 }}>
            {!isRunButtonLoading ? (
              <Button
                key="runButton"
                disabled={isRunButtonDisabled}
                onClick={onRunHandler}
                size="medium"
                startIcon={<PlayCircleIcon />}
                sx={{
                  minWidth: "120px",
                  bgcolor: "#F79191",
                  "&:hover": { bgcolor: "#FFCCCC" },
                }}
                variant="contained"
              >
                {t("run_button")}
              </Button>
            ) : (
              <LoadingButton
                loading={isRunButtonLoading}
                loadingPosition="center"
                sx={{ minWidth: "120px" }}
                color="secondary"
                variant="contained"
              >
                {t("run_loading_button")}
              </LoadingButton>
            )}
          </Box>
        </Grid>

        {/* Alert message section */}
        {message && showMessage && (
          <AlertMessage
            handleCloseMessage={handleCloseMessage}
            message={message}
            severity={severity}
            showMessage={showMessage}
          />
        )}
      </Box>
    </>
  );
};

export default DataInput;
