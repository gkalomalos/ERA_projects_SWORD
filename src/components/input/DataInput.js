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

import AlertMessage from "../alerts/AlertMessage";

const DataInput = (props) => {
  const { t } = useTranslation();

  const [isRunButtonLoading, setIsRunButtonLoading] = useState(false);
  const [isRunButtonDisabled, setIsRunButtonDisabled] = useState(true);
  const [message, setMessage] = useState("");
  const [severity, setSeverity] = useState("info");
  const [showMessage, setShowMessage] = useState(true);

  const onRunHandler = () => {
    const body = {
      annualPopulationGrowth: props.selectedAnnualPopulationGrowth,
      annualGDPGrowth: props.selectedAnnualGDPGrowth,
      countryName: props.selectedCountry,
      exposureEconomic: props.selectedExposureEconomic,
      exposureFile: props.selectedExposureFile,
      exposureNonEconomic: props.selectedExposureNonEconomic,
      hazardType: props.selectedHazard,
      isEra: props.selectedAppOption === "era" ? true : false,
      hazardFile: props.selectedHazardFile,
      scenario: props.selectedScenario,
      timeHorizon: props.selectedTimeHorizon,
    };
    setIsRunButtonDisabled(true);
    setIsRunButtonLoading(true);
    props.onScenarioRunning(true);
    APIService.Run(body)
      .then((response) => {
        setMessage(response.result.status.message);
        response.result.status.code === 2000 ? setSeverity("success") : setSeverity("error");
        setShowMessage(true);
        setIsRunButtonLoading(false);
        setIsRunButtonDisabled(false);
        props.onChangeMapTitle(response.result.data.mapTitle);
        props.onScenarioRunning(false);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  const handleCloseMessage = () => {
    setShowMessage(false);
  };

  const onCardClickHandler = (card) => {
    props.onChangeCard(card);
  };

  const handleRunButton = () => {
    if (
      props.selectedCountry &&
      props.selectedHazard &&
      props.selectedScenario &&
      (props.selectedExposureEconomic || props.selectedExposureNonEconomic) &&
      props.isValidHazard &&
      (props.isValidExposureEconomic || props.isValidExposureNonEconomic)
    ) {
      setIsRunButtonDisabled(false);
    } else {
      setIsRunButtonDisabled(true);
    }
  };

  useEffect(() => {
    handleRunButton();
  }, [props]);

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
              onSelectTab={props.onSelectTab}
              selectedCountry={props.selectedCountry}
            />
          </Grid>
          <Grid item xs={12}>
            <Hazard
              isValidHazard={props.isValidHazard}
              onCardClick={onCardClickHandler}
              onSelectTab={props.onSelectTab}
              selectedHazard={props.selectedHazard}
            />
          </Grid>
          <Grid item xs={12}>
            <Scenario
              onCardClick={onCardClickHandler}
              onSelectTab={props.onSelectTab}
              selectedScenario={props.selectedScenario}
            />
          </Grid>
          <Grid item xs={12}>
            <TimeHorizon
              onCardClick={onCardClickHandler}
              onSelectTab={props.onSelectTab}
              selectedAppOption={props.selectedAppOption}
              selectedCountry={props.selectedCountry}
              selectedTimeHorizon={props.selectedTimeHorizon}
            />
          </Grid>
          <Grid item xs={12}>
            <AnnualGrowth
              onCardClick={onCardClickHandler}
              selectedAppOption={props.selectedAppOption}
              selectedCountry={props.selectedCountry}
              onSelectTab={props.onSelectTab}
              selectedAnnualGDPGrowth={props.selectedAnnualGDPGrowth}
              selectedAnnualPopulationGrowth={props.selectedAnnualPopulationGrowth}
            />
          </Grid>
          <Grid item xs={12}>
            <ExposureEconomic
              isValidExposureEconomic={props.isValidExposureEconomic}
              onCardClick={onCardClickHandler}
              onSelectTab={props.onSelectTab}
              selectedExposureEconomic={props.selectedExposureEconomic}
              selectedExposureNonEconomic={props.selectedExposureNonEconomic}
            />
          </Grid>
          <Grid item xs={12}>
            <ExposureNonEconomic
              isValidExposureNonEconomic={props.isValidExposureNonEconomic}
              onCardClick={onCardClickHandler}
              onSelectTab={props.onSelectTab}
              selectedExposureEconomic={props.selectedExposureEconomic}
              selectedExposureNonEconomic={props.selectedExposureNonEconomic}
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
