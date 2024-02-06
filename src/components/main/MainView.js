import React, { useState } from "react";

import ChartLayout from "../controls/ChartLayout";
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
          selectedAnnualGDPGrowth={props.selectedAnnualGDPGrowth}
          selectedAnnualPopulationGrowth={props.selectedAnnualPopulationGrowth}
          selectedCard={props.selectedCard}
          selectedCountry={props.selectedCountry}
          selectedExposureEconomic={props.selectedExposureEconomic}
          selectedExposureNonEconomic={props.selectedExposureNonEconomic}
          selectedHazard={props.selectedHazard}
          selectedScenario={props.selectedScenario}
          selectedTimeHorizon={props.selectedTimeHorizon}
          onChangeCountry={props.onChangeCountry}
          onChangeExposureEconomic={props.onChangeExposureEconomic}
          onChangeExposureNonEconomic={props.onChangeExposureNonEconomic}
          onChangeHazard={props.onChangeHazard}
          onChangeScenario={props.onChangeScenario}
          onChangeTimeHorizon={props.onChangeTimeHorizon}
          onChangeAnnualGDPGrowth={props.onChangeAnnualGDPGrowth}
          onChangeAnnualPopulationGrowth={props.onChangeAnnualPopulationGrowth}
          onChangeValidEconomicExposure={props.onChangeValidEconomicExposure}
          onChangeValidNonEconomicExposure={props.onChangeValidNonEconomicExposure}
          onChangeValidHazard={props.onChangeValidHazard}
        />
      )}
      {/* Render the main layout with the Economic & Non-Economic section according to each sub tab selected  */}
      {/* Render MapLayout component */}
      {props.selectedTab === 1 && (
        <>
          {viewControl === "display_map" && (
            <MapLayout selectedCountry={props.selectedCountry} activeMap={props.activeMap} />
          )}
          {viewControl === "display_chart" && <ChartLayout />}
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
