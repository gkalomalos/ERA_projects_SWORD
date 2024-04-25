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

const MainView = (props) => {
  const [viewControl, setViewControl] = useState("display_map");

  const setViewControlHandler = (control) => {
    setViewControl(control);
  };

  return (
    <>
      {<MainViewTitle selectedTab={props.selectedTab} mapTitle={props.mapTitle} />}
      {/* Render the main layout with the Parameters section according to each input selected  */}
      {props.selectedTab === 0 && (
        <ViewCard
          selectedAnnualGrowth={props.selectedAnnualGrowth}
          selectedAppOption={props.selectedAppOption}
          selectedCard={props.selectedCard}
          selectedCountry={props.selectedCountry}
          selectedExposureEconomic={props.selectedExposureEconomic}
          selectedExposureFile={props.selectedExposureFile}
          selectedExposureNonEconomic={props.selectedExposureNonEconomic}
          selectedHazard={props.selectedHazard}
          selectedHazardFile={props.selectedHazardFile}
          selectedScenario={props.selectedScenario}
          selectedTimeHorizon={props.selectedTimeHorizon}
          onChangeCountry={props.onChangeCountry}
          onChangeExposureEconomic={props.onChangeExposureEconomic}
          onChangeExposureFile={props.onChangeExposureFile}
          onChangeExposureNonEconomic={props.onChangeExposureNonEconomic}
          onChangeHazard={props.onChangeHazard}
          onChangeHazardFile={props.onChangeHazardFile}
          onChangeScenario={props.onChangeScenario}
          onChangeTimeHorizon={props.onChangeTimeHorizon}
          onChangeAnnualGrowth={props.onChangeAnnualGrowth}
          onChangeValidEconomicExposure={props.onChangeValidEconomicExposure}
          onChangeValidNonEconomicExposure={props.onChangeValidNonEconomicExposure}
          onChangeValidHazard={props.onChangeValidHazard}
        />
      )}
      {/* Render the main layout with the Economic & Non-Economic section according to each sub tab selected  */}
      {/* Render Economic & non-Economic - Risk view */}
      {props.selectedTab === 1 && props.selectedSubTab === 0 && (
        <>
          {viewControl === "display_map" && (
            <MapLayout selectedCountry={props.selectedCountry} activeMap={props.activeMap} />
          )}
          {viewControl === "display_chart" && <RiskChartLayout />}
          {viewControl === "settings" && <SettingsView />}
          {viewControl === "progress" && <ProgressView />}
          <MainViewControls onChangeViewControls={setViewControlHandler} />
        </>
      )}
      {/* Render Economic & non-Economic - Adaptation view */}
      {props.selectedTab === 1 && props.selectedSubTab === 1 && (
        <>
          {viewControl === "display_map" && <AdaptationMap />}
          {viewControl === "display_chart" && <AdaptationChartLayout />}
          {viewControl === "settings" && <SettingsView />}
          {viewControl === "progress" && <ProgressView />}
          <MainViewControls onChangeViewControls={setViewControlHandler} />
        </>
      )}
      {props.selectedTab === 2 && (
        <>
          <PageUnderConstructionView />
        </>
      )}
      {props.selectedTab === 3 && (
        <>
          <PageUnderConstructionView />
        </>
      )}
    </>
  );
};

export default MainView;