import React, { useState, useEffect } from "react";

import { Grid } from "@mui/material";

import AdaptationMeasuresInput from "./components/input/AdaptationMeasuresInput";
import DataInput from "./components/input/DataInput";
import Header from "./components/nav/Header";
import LoadModal from "./components/loaders/LoadModal";
import MainTabs from "./components/main/MainTabs";
import MainView from "./components/main/MainView";
import ResultsView from "./components/results/ResultsView";

import NavigateAlert from "./components/alerts/NavigateAlert";

const App = () => {
  const [activeMap, setActiveMap] = useState("hazard");
  const [isScenarioRunning, setIsScenarioRunning] = useState(false);
  const [isValidExposureEconomic, setIsValidExposureEconomic] = useState(false);
  const [isValidExposureNonEconomic, setIsValidExposureNonEconomic] = useState(false);
  const [isValidHazard, setIsValidHazard] = useState(false);
  const [mapTitle, setMapTitle] = useState("");
  const [modalMessage, setModalMessage] = useState("");
  const [selectedAnnualGDPGrowth, setSelectedAnnualGDPGrowth] = useState(0);
  const [selectedAnnualPopulationGrowth, setSelectedAnnualPopulationGrowth] = useState(0);
  const [selectedAppOption, setSelectedAppOption] = useState("");
  const [selectedCard, setSelectedCard] = useState("country");
  const [selectedCountry, setSelectedCountry] = useState("");
  const [selectedExposureEconomic, setSelectedExposureEconomic] = useState("");
  const [selectedExposureFile, setSelectedExposureFile] = useState("");
  const [selectedExposureNonEconomic, setSelectedExposureNonEconomic] = useState("");
  const [selectedHazard, setSelectedHazard] = useState("");
  const [selectedHazardFile, setSelectedHazardFile] = useState("");
  const [selectedScenario, setSelectedScenario] = useState("");
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedSubTab, setSelectedSubTab] = useState(0);
  const [selectedTimeHorizon, setSelectedTimeHorizon] = useState(2024);

  const setMapTitleHandler = (data) => {
    setMapTitle(data);
  };

  const setSelectedAppOptionHandler = (option) => {
    setSelectedAppOption(option);
  };

  const setIsScenarioRunningHandler = (data) => {
    setIsScenarioRunning(data);
  };

  const setSelectedCountryHandler = (country) => {
    setSelectedCountry(country);
  };

  const setSelectedExposureEconomicHandler = (exposureEconomic) => {
    setSelectedExposureEconomic(exposureEconomic);
  };

  const setSelectedExposureFileHandler = (exposureFile) => {
    setSelectedExposureFile(exposureFile);
  };

  const setValidExposureEconomicHandler = (isValid) => {
    if (selectedAppOption === "era") {
      setIsValidExposureEconomic(true);
    } else {
      setIsValidExposureEconomic(isValid);
    }
  };

  const setValidExposureNonEconomicHandler = (isValid) => {
    if (selectedAppOption === "era") {
      setIsValidExposureNonEconomic(true);
    } else {
      setIsValidExposureNonEconomic(isValid);
    }
  };

  const setValidHazardHandler = (isValid) => {
    if (selectedAppOption === "era") {
      setIsValidHazard(true);
    } else {
      setIsValidHazard(isValid);
    }
  };

  const setSelectedExposureNonEconomicHandler = (exposureNonEconomic) => {
    setSelectedExposureNonEconomic(exposureNonEconomic);
  };

  const setSelectedHazardHandler = (hazard) => {
    setSelectedHazard(hazard);
  };

  const setSelectedHazardFileHandler = (hazardFile) => {
    setSelectedHazardFile(hazardFile);
  };

  const setSelectedScenarioHandler = (scenario) => {
    setSelectedScenario(scenario);
  };

  const setSelectedTimeHorizonHandler = (timeHorizon) => {
    setSelectedTimeHorizon(timeHorizon);
  };

  const setSelectedAnnualPopulationGrowthHandler = (annualPopulationGrowth) => {
    setSelectedAnnualPopulationGrowth(annualPopulationGrowth);
  };

  const setSelectedAnnualGDPGrowthHandler = (annualGDPGrowth) => {
    setSelectedAnnualGDPGrowth(annualGDPGrowth);
  };

  const setSelectedCardHandler = (card) => {
    setSelectedCard(card);
  };

  const setSelectedTabHandler = (tab) => {
    setSelectedTab(tab);
    setSelectedSubTab(0);
  };

  const setSelectedSubTabHandler = (subTab) => {
    setSelectedSubTab(subTab);
  };

  const setActiveMapHandler = (map) => {
    setActiveMap(map);
  };

  // Reset states when selectedCountry changes
  useEffect(() => {
    setSelectedAnnualPopulationGrowth(0);
    setSelectedAnnualGDPGrowth(0);
    setSelectedExposureEconomic("");
    setSelectedExposureFile("");
    setSelectedExposureNonEconomic("");
    setSelectedHazard("");
    setSelectedHazardFile("");
    setSelectedScenario("");
    setSelectedTimeHorizon(2024);
    setValidExposureEconomicHandler(false);
    setValidExposureNonEconomicHandler(false);
    setValidHazardHandler(false);
  }, [selectedCountry]);

  useEffect(() => {
    const progressListener = (event, data) => {
      setModalMessage(data.message);
    };
    window.electron.on("progress", progressListener);
    return () => {
      window.electron.remove("progress", progressListener);
    };
  }, []);

  return (
    <>
      {selectedAppOption === "" ? (
        <NavigateAlert
          onChangeOption={setSelectedAppOptionHandler}
          selectedOption={selectedAppOption}
        />
      ) : (
        <>
          <Header />
          <MainTabs
            onChangeTab={setSelectedTabHandler}
            onChangeSubTab={setSelectedSubTabHandler}
            propSelectedSubTab={selectedSubTab}
            propSelectedTab={selectedTab}
          />
          <Grid container spacing={2} style={{ padding: "16px", height: "calc(100vh - 64px)" }}>
            <Grid item xs={12} md={2}>
              {(selectedTab === 0 || (selectedTab === 1 && selectedSubTab === 0)) && (
                <DataInput
                  isValidExposureEconomic={isValidExposureEconomic}
                  isValidExposureNonEconomic={isValidExposureNonEconomic}
                  isValidHazard={isValidHazard}
                  onChangeCard={setSelectedCardHandler}
                  onChangeMapTitle={setMapTitleHandler}
                  onScenarioRunning={setIsScenarioRunningHandler}
                  onSelectTab={setSelectedTabHandler}
                  selectedAnnualPopulationGrowth={selectedAnnualPopulationGrowth}
                  selectedAnnualGDPGrowth={selectedAnnualGDPGrowth}
                  selectedCountry={selectedCountry}
                  selectedExposureEconomic={selectedExposureEconomic}
                  selectedExposureFile={selectedExposureFile}
                  selectedExposureNonEconomic={selectedExposureNonEconomic}
                  selectedHazard={selectedHazard}
                  selectedHazardFile={selectedHazardFile}
                  selectedScenario={selectedScenario}
                  selectedTimeHorizon={selectedTimeHorizon}
                />
              )}
              {selectedTab === 1 && selectedSubTab === 1 && (
                <AdaptationMeasuresInput selectedHazard={selectedHazard} />
              )}
            </Grid>
            <Grid item xs={12} md={selectedTab !== 0 ? 8 : 10}>
              <MainView
                activeMap={activeMap}
                mapTitle={mapTitle}
                selectedAnnualGDPGrowth={selectedAnnualGDPGrowth}
                selectedAnnualPopulationGrowth={selectedAnnualPopulationGrowth}
                selectedAppOption={selectedAppOption}
                selectedCard={selectedCard}
                selectedCountry={selectedCountry}
                selectedExposureEconomic={selectedExposureEconomic}
                selectedExposureFile={selectedExposureFile}
                selectedExposureNonEconomic={selectedExposureNonEconomic}
                selectedHazard={selectedHazard}
                selectedHazardFile={selectedHazardFile}
                selectedScenario={selectedScenario}
                selectedTimeHorizon={selectedTimeHorizon}
                selectedTab={selectedTab}
                selectedSubTab={selectedSubTab}
                onChangeActiveMap={setActiveMapHandler}
                onChangeAnnualPopulationGrowth={setSelectedAnnualPopulationGrowthHandler}
                onChangeAnnualGDPGrowth={setSelectedAnnualGDPGrowthHandler}
                onChangeCountry={setSelectedCountryHandler}
                onChangeExposureEconomic={setSelectedExposureEconomicHandler}
                onChangeExposureFile={setSelectedExposureFileHandler}
                onChangeExposureNonEconomic={setSelectedExposureNonEconomicHandler}
                onChangeHazard={setSelectedHazardHandler}
                onChangeHazardFile={setSelectedHazardFileHandler}
                onChangeScenario={setSelectedScenarioHandler}
                onChangeTimeHorizon={setSelectedTimeHorizonHandler}
                onChangeValidEconomicExposure={setValidExposureEconomicHandler}
                onChangeValidNonEconomicExposure={setValidExposureNonEconomicHandler}
                onChangeValidHazard={setValidHazardHandler}
              />
            </Grid>

            {selectedTab !== 0 && (
              <Grid item xs={12} md={2}>
                <ResultsView selectedTab={selectedTab} onChangeActiveMap={setActiveMapHandler} />
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
