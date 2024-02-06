import React, { useState } from "react";
import { useTranslation } from "react-i18next";

import { Box, Button } from "@mui/material";
import LoadingButton from "@mui/lab/LoadingButton";
import PlayCircleIcon from "@mui/icons-material/PlayCircle";

import APIService from "../../APIService";

const RunScenario = (props) => {
  const { t } = useTranslation();

  const [isRunButtonLoading, setIsRunButtonLoading] = useState(false);
  const [isRunButtonDisabled, setIsRunButtonDisabled] = useState(false);
  const [message, setMessage] = useState("");
  const [severity, setSeverity] = useState("info");
  const [showMessage, setShowMessage] = useState(true);

  const onRunHandler = () => {
    const body = {
      annualGrowth: props.selectedAnnualPopulationGrowth,
      country: props.selectedCountry,
      exposure: props.selectedExposure,
      hazard: props.selectedHazard,
      scenario: props.selectedScenario,
      timeHorizon: props.selectedTimeHorizon,
    };
    setIsRunButtonDisabled(true);
    setIsRunButtonLoading(true);
    props.onScenarioRunning(true);
    console.log(body);
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

  return (
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
            bgcolor: "#FFCCCC",
            "&:hover": { bgcolor: "#F79191" },
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
  );
};

export default RunScenario;
