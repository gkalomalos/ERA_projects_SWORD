import React, { useState } from "react";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";

import { Box, Button } from "@mui/material";
import LoadingButton from "@mui/lab/LoadingButton";
import PlayCircleIcon from "@mui/icons-material/PlayCircle";

import APIService from "../../APIService";

const RunScenario = ({
  onChangeMapTitle,
  onScenarioRunning,
  selectedAnnualGrowth,
  selectedCountry,
  selectedExposure,
  selectedHazard,
  selectedScenario,
  selectedTimeHorizon,
}) => {
  const { t } = useTranslation();

  const [isRunButtonLoading, setIsRunButtonLoading] = useState(false);
  const [isRunButtonDisabled, setIsRunButtonDisabled] = useState(false);

  const onRunHandler = () => {
    const body = {
      annualGrowth: selectedAnnualGrowth,
      country: selectedCountry,
      exposure: selectedExposure,
      hazard: selectedHazard,
      scenario: selectedScenario,
      timeHorizon: selectedTimeHorizon,
    };
    setIsRunButtonDisabled(true);
    setIsRunButtonLoading(true);
    onScenarioRunning(true);
    APIService.Run(body)
      .then((response) => {
        setIsRunButtonLoading(false);
        setIsRunButtonDisabled(false);
        onChangeMapTitle(response.result.data.mapTitle);
        onScenarioRunning(false);
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

RunScenario.propTypes = {
  onChangeMapTitle: PropTypes.func.isRequired,
  onScenarioRunning: PropTypes.func.isRequired,
  selectedAnnualGrowth: PropTypes.number.isRequired,
  selectedCountry: PropTypes.string.isRequired,
  selectedExposure: PropTypes.string.isRequired,
  selectedHazard: PropTypes.string.isRequired,
  selectedScenario: PropTypes.string.isRequired,
  selectedTimeHorizon: PropTypes.array.isRequired,
};

export default RunScenario;
