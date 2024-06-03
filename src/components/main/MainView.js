import React, { useState } from "react";

import AdaptationMap from "../map/AdaptationMap";
import AdaptationChartLayout from "../controls/AdaptationChartLayout";
import RiskChartLayout from "../controls/RiskChartLayout";
import MainViewControls from "../controls/MainViewControls";
import MainViewTitle from "../title/MainViewTitle";
import MapLayout from "../map/MapLayout";
import ProgressView from "../controls/ProgressView";
import SettingsView from "../controls/SettingsView";
import ViewCard from "../cards/ViewCard";
import PageUnderConstructionView from "../misc/PageUnderConstructionView";
import ReportsView from "../reports/ReportsView";
import useStore from "../../store";

const MainView = () => {
  const {
    activeMap,
    selectedAnnualGrowth,
    selectedAppOption,
    selectedCard,
    selectedCountry,
    selectedExposureEconomic,
    selectedExposureFile,
    selectedExposureNonEconomic,
    selectedHazard,
    selectedHazardFile,
    selectedScenario,
    selectedSubTab,
    selectedTab,
    selectedTimeHorizon,
    setSelectedCountry,
    setSelectedExposureEconomic,
    setSelectedExposureFile,
    setSelectedExposureNonEconomic,
    setSelectedHazard,
    setSelectedHazardFile,
    setSelectedScenario,
    setSelectedTimeHorizon,
    setSelectedAnnualGrowth,
    setIsValidExposureEconomic,
    setIsValidExposureNonEconomic,
    setIsValidHazard,
  } = useStore();

  const [viewControl, setViewControl] = useState("display_map");

  const setViewControlHandler = (control) => {
    setViewControl(control);
  };

  return (
    <>
      {<MainViewTitle />}
      {selectedTab === 0 && (
        <ViewCard
          selectedAnnualGrowth={selectedAnnualGrowth}
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
          onChangeCountry={setSelectedCountry}
          onChangeExposureEconomic={setSelectedExposureEconomic}
          onChangeExposureFile={setSelectedExposureFile}
          onChangeExposureNonEconomic={setSelectedExposureNonEconomic}
          onChangeHazard={setSelectedHazard}
          onChangeHazardFile={setSelectedHazardFile}
          onChangeScenario={setSelectedScenario}
          onChangeTimeHorizon={setSelectedTimeHorizon}
          onChangeAnnualGrowth={setSelectedAnnualGrowth}
          onChangeValidEconomicExposure={setIsValidExposureEconomic}
          onChangeValidNonEconomicExposure={setIsValidExposureNonEconomic}
          onChangeValidHazard={setIsValidHazard}
        />
      )}
      {selectedTab === 1 && selectedSubTab === 0 && (
        <>
          {viewControl === "display_map" && (
            <MapLayout selectedCountry={selectedCountry} activeMap={activeMap} />
          )}
          {viewControl === "display_chart" && <RiskChartLayout />}
          {viewControl === "settings" && <SettingsView />}
          {viewControl === "progress" && <ProgressView />}
          <MainViewControls onChangeViewControls={setViewControlHandler} />
        </>
      )}
      {selectedTab === 1 && selectedSubTab === 1 && (
        <>
          {viewControl === "display_map" && <AdaptationMap />}
          {viewControl === "display_chart" && <AdaptationChartLayout />}
          {viewControl === "settings" && <SettingsView />}
          {viewControl === "progress" && <ProgressView />}
          <MainViewControls onChangeViewControls={setViewControlHandler} />
        </>
      )}
      {selectedTab === 2 && (
        <>
          <PageUnderConstructionView />
        </>
      )}
      {selectedTab === 3 && (
        <>
          <ReportsView />
        </>
      )}
    </>
  );
};

export default MainView;
