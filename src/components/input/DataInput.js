import React, { useState } from "react";

import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import MuiAlert from "@mui/material/Alert";
import LoadingButton from "@mui/lab/LoadingButton";
import PlayCircleIcon from "@mui/icons-material/PlayCircle";
import Snackbar from "@mui/material/Snackbar";
import Stack from "@mui/material/Stack";

import APIService from "../../APIService";
import AnnualGrowth from "./AnnualGrowth";
import Country from "./Country";
import Exposure from "./Exposure";
import Hazard from "./Hazard";
import Scenario from "./Scenario";
import TimeHorizon from "./TimeHorizon";

const DataInput = (props) => {
  const [annualGrowth, setAnnualGrowth] = useState(0);
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [exposure, setExposure] = useState({ file: "", value: [] });
  const [exposureCheck, setExposureCheck] = useState("select");
  const [hazard, setHazard] = useState({ file: "", value: "" });
  const [hazardCheck, setHazardCheck] = useState("select");
  const [isRunButtonLoading, setIsRunButtonLoading] = useState(false);
  const [isRunButtonDisabled, setIsRunButtonDisabled] = useState(false);
  const [message, setMessage] = useState("");
  const [scenarioCheck, setScenarioCheck] = useState("historical");
  const [scenario, setScenario] = useState("");
  const [severity, setSeverity] = useState("info");
  const [showMessage, setShowMessage] = useState(true);
  const [timeHorizon, setTimeHorizon] = useState("");

  const onRunHandler = () => {
    const body = {
      annualGrowth: annualGrowth,
      exposure: exposure,
      hazard: hazard,
      scenario: scenario,
      timeHorizon: timeHorizon,
    };
    setIsRunButtonDisabled(true);
    setIsRunButtonLoading(true);
    props.onScenarioRunning(true);
    APIService.Run(body)
      .then((response) => {
        setMessage(response.result.status.message);
        response.result.status.code === 2000
          ? setSeverity("success")
          : setSeverity("error");
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

  const handleChipDelete = (e, value) => {
    e.preventDefault();
    setExposure({
      file: "",
      value: exposure.value.filter((country) => country !== value),
    });
  };

  const onSelectExposureHandler = (event) => {
    const {
      target: { value },
    } = event;
    setExposure({
      file: "",
      value: typeof value === "string" ? value.split(",") : value,
    });
  };

  const onSelectCountryHandler = (event) => {
    setSelectedCountry(event.target.value);
  };

  const onSelectHazardHandler = (event) => {
    setHazard({ file: "", value: event.target.value });
  };

  const onSelectTimeHorizonHandler = (event) => {
    setTimeHorizon(event.target.value);
  };

  const handleCloseMessage = () => {
    setShowMessage(false);
  };

  const onChangeExposureRadioButtonHandler = (event) => {
    setExposureCheck(event.target.value);
  };

  const onChangeHazardRadioButtonHandler = (event) => {
    setHazardCheck(event.target.value);
  };

  const onLoadChangeExposureHandler = (event) => {
    setExposure({ file: event.target.files[0].name, value: [] });
  };

  const onLoadChangeHazardHandler = (event) => {
    setHazard({ file: event.target.files[0].name, value: [] });
  };

  const onChangeScenarioRadioButtonHandler = (event) => {
    setScenarioCheck(event.target.value);
  };

  const onAnnualGrowthChangeHandler = (event) => {
    setAnnualGrowth(event.target.value);
  };

  const onScenarioChangeHandler = (event) => {
    setScenario(event.target.value);
  };

  const Alert = React.forwardRef(function Alert(props, ref) {
    return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
  });

  const Message = () => {
    return (
      <Stack spacing={2} sx={{ width: "100%" }}>
        <Snackbar
          open={showMessage}
          autoHideDuration={6000}
          onClose={handleCloseMessage}
          anchorOrigin={{ vertical: "bottom", horizontal: "center" }}
        >
          <Alert
            onClose={handleCloseMessage}
            severity={severity}
            sx={{ width: "100%" }}
          >
            {message}
          </Alert>
        </Snackbar>
      </Stack>
    );
  };

  return (
    <>
      <Country
        selectedCountry={selectedCountry}
        onCountryChange={onSelectCountryHandler}
      />
      <Exposure
        chipDelete={handleChipDelete}
        defaultValue={exposureCheck}
        exposureCheck={exposureCheck}
        onChangeRadio={onChangeExposureRadioButtonHandler}
        onChangeSelect={onSelectExposureHandler}
        onLoadChange={onLoadChangeExposureHandler}
        value={exposure.value}
      />
      <Hazard
        defaultValue={hazardCheck}
        hazardCheck={hazardCheck}
        onChangeRadio={onChangeHazardRadioButtonHandler}
        onSelectChange={onSelectHazardHandler}
        onLoadChange={onLoadChangeHazardHandler}
        value={hazard.value}
      />
      <Scenario
        onChange={onScenarioChangeHandler}
        onChangeRadio={onChangeScenarioRadioButtonHandler}
        scenarioCheck={scenarioCheck}
        value={scenario}
      />
      <TimeHorizon
        onSelectChange={onSelectTimeHorizonHandler}
        value={timeHorizon}
      />
      <AnnualGrowth onChange={onAnnualGrowthChangeHandler} />
      <Box sx={{ width: 350 }} textAlign="center">
        {!isRunButtonLoading && (
          <Button
            disabled={isRunButtonDisabled}
            onClick={onRunHandler}
            size="medium"
            startIcon={<PlayCircleIcon />}
            sx={{
              minWidth: "120px",
              maxWidth: "120px",
              bgcolor: "#2A4D69",
              "&:hover": { bgcolor: "5c87b1" },
            }}
            variant="contained"
          >
            Run
          </Button>
        )}
        {isRunButtonLoading && (
          <LoadingButton
            loading={isRunButtonLoading}
            loadingPosition="center"
            sx={{ minWidth: "120px", maxWidth: "120px" }}
            color="secondary"
            variant="contained"
          >
            Run...
          </LoadingButton>
        )}
      </Box>
      {showMessage && message !== "" && <Message />}
    </>
  );
};

export default DataInput;
