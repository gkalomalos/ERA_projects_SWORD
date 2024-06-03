import React, { useEffect } from "react";

import { Grid } from "@mui/material";

import AdaptationMeasuresInput from "./components/input/AdaptationMeasuresInput";
import DataInput from "./components/input/DataInput";
import Header from "./components/nav/Header";
import LoadModal from "./components/loaders/LoadModal";
import MainTabs from "./components/main/MainTabs";
import MainView from "./components/main/MainView";
import NavigateAlert from "./components/alerts/NavigateAlert";
import ResultsView from "./components/results/ResultsView";
import useStore from "./store";

const App = () => {
  const {
    isScenarioRunning,
    modalMessage,
    selectedAppOption,
    selectedCountry,
    selectedExposureEconomic,
    selectedExposureNonEconomic,
    selectedHazard,
    selectedTab,
    selectedSubTab,
    setActiveMap,
    setSelectedAnnualGrowth,
    setSelectedExposureEconomic,
    setSelectedExposureFile,
    setSelectedExposureNonEconomic,
    setSelectedHazard,
    setSelectedHazardFile,
    setSelectedScenario,
    setSelectedTimeHorizon,
    setIsValidExposureEconomic,
    setIsValidExposureNonEconomic,
    setIsValidHazard,
    setModalMessage,
  } = useStore();

  useEffect(() => {
    setSelectedAnnualGrowth(0);
    setSelectedExposureEconomic("");
    setSelectedExposureFile("");
    setSelectedExposureNonEconomic("");
    setSelectedHazard("");
    setSelectedHazardFile("");
    setSelectedScenario("");
    setSelectedTimeHorizon([2024, 2050]);
    setIsValidExposureEconomic(false);
    setIsValidExposureNonEconomic(false);
    setIsValidHazard(false);
  }, [selectedCountry]);

  useEffect(() => {
    setSelectedScenario("");
  }, [selectedHazard]);

  useEffect(() => {
    setSelectedAnnualGrowth(0);
  }, [selectedExposureEconomic, selectedExposureNonEconomic]);

  useEffect(() => {
    const progressListener = (event, data) => {
      setModalMessage(data.message);
    };
    try {
      window.electron.on("progress", progressListener);
      return () => {
        window.electron.remove("progress", progressListener);
      };
    } catch (e) {
      console.log("Not running in electron");
    }
  }, []);

  return (
    <>
      {selectedAppOption === "" ? (
        <NavigateAlert />
      ) : (
        <>
          <Header />
          <MainTabs />
          <Grid
            container
            spacing={2}
            style={{
              padding: "16px",
              paddingTop: "174px",
              overflow: "auto",
            }}
          >
            <Grid item xs={12} md={2}>
              {(selectedTab === 0 || (selectedTab === 1 && selectedSubTab === 0)) && <DataInput />}
              {selectedTab === 1 && selectedSubTab === 1 && <AdaptationMeasuresInput />}
            </Grid>
            <Grid item xs={12} md={selectedTab !== 0 ? 8 : 10}>
              <MainView />
            </Grid>
            {selectedTab !== 0 && (
              <Grid item xs={12} md={2}>
                <ResultsView selectedTab={selectedTab} onChangeActiveMap={setActiveMap} />
              </Grid>
            )}
          </Grid>
          {isScenarioRunning && <LoadModal message={modalMessage} open={isScenarioRunning} />}
        </>
      )}
    </>
  );
};

export default App;
