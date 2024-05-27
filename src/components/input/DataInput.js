import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
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

import AlertMessage from "../alerts/AlertMessage";

const DataInput = ({
  isValidExposureEconomic,
  isValidExposureNonEconomic,
  isValidHazard,
  onChangeCard,
  onChangeMapTitle,
  onScenarioRunning,
  onSelectTab,
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
}) => {
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
    onScenarioRunning(true);
    APIService.Run(body)
      .then((response) => {
        setMessage(response.result.status.message);
        response.result.status.code === 2000 ? setSeverity("success") : setSeverity("error");
        setShowMessage(true);
        setIsRunButtonLoading(false);
        setIsRunButtonDisabled(false);
        onChangeMapTitle(response.result.data.mapTitle);
        onScenarioRunning(false);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  const handleCloseMessage = () => {
    setShowMessage(false);
  };

  const onCardClickHandler = (card) => {
    onChangeCard(card);
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
    isValidExposureEconomic,
    isValidExposureNonEconomic,
    isValidHazard,
    onChangeCard,
    onChangeMapTitle,
    onScenarioRunning,
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
              onSelectTab={onSelectTab}
              selectedCountry={selectedCountry}
            />
          </Grid>
          <Grid item xs={12}>
            <Hazard
              isValidHazard={isValidHazard}
              onCardClick={onCardClickHandler}
              onSelectTab={onSelectTab}
              selectedHazard={selectedHazard}
            />
          </Grid>
          <Grid item xs={12}>
            <Scenario
              onCardClick={onCardClickHandler}
              onSelectTab={onSelectTab}
              selectedScenario={selectedScenario}
            />
          </Grid>
          <Grid item xs={12}>
            <TimeHorizon
              onCardClick={onCardClickHandler}
              onSelectTab={onSelectTab}
              selectedAppOption={selectedAppOption}
              selectedCountry={selectedCountry}
              selectedTimeHorizon={selectedTimeHorizon}
            />
          </Grid>
          <Grid item xs={12}>
            <ExposureEconomic
              isValidExposureEconomic={isValidExposureEconomic}
              onCardClick={onCardClickHandler}
              onSelectTab={onSelectTab}
              selectedExposureEconomic={selectedExposureEconomic}
              selectedExposureNonEconomic={selectedExposureNonEconomic}
            />
          </Grid>
          <Grid item xs={12}>
            <ExposureNonEconomic
              isValidExposureNonEconomic={isValidExposureNonEconomic}
              onCardClick={onCardClickHandler}
              onSelectTab={onSelectTab}
              selectedExposureEconomic={selectedExposureEconomic}
              selectedExposureNonEconomic={selectedExposureNonEconomic}
            />
          </Grid>
          <Grid item xs={12}>
            <AnnualGrowth
              onCardClick={onCardClickHandler}
              onSelectTab={onSelectTab}
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

DataInput.propTypes = {
  isValidExposureEconomic: PropTypes.bool.isRequired,
  isValidExposureNonEconomic: PropTypes.bool.isRequired,
  isValidHazard: PropTypes.bool.isRequired,
  onChangeCard: PropTypes.func.isRequired,
  onChangeMapTitle: PropTypes.func.isRequired,
  onScenarioRunning: PropTypes.func.isRequired,
  onSelectTab: PropTypes.func.isRequired,

  selectedAnnualGrowth: PropTypes.number.isRequired,
  selectedAppOption: PropTypes.string.isRequired,
  selectedCountry: PropTypes.string.isRequired,
  selectedExposureEconomic: PropTypes.string.isRequired,
  selectedExposureFile: PropTypes.string.isRequired,
  selectedExposureNonEconomic: PropTypes.string.isRequired,
  selectedHazard: PropTypes.string.isRequired,
  selectedHazardFile: PropTypes.string.isRequired,
  selectedScenario: PropTypes.string.isRequired,
  selectedTimeHorizon: PropTypes.array.isRequired,
};

export default DataInput;
