import React, { useState } from "react";
import PropTypes from "prop-types";

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

const MainView = ({
  activeMap,
  mapTitle,
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
  onChangeCountry,
  onChangeExposureEconomic,
  onChangeExposureFile,
  onChangeExposureNonEconomic,
  onChangeHazard,
  onChangeHazardFile,
  onChangeScenario,
  onChangeTimeHorizon,
  onChangeAnnualGrowth,
  onChangeValidEconomicExposure,
  onChangeValidNonEconomicExposure,
  onChangeValidHazard,
}) => {
  const [viewControl, setViewControl] = useState("display_map");

  const setViewControlHandler = (control) => {
    setViewControl(control);
  };

  return (
    <>
      {<MainViewTitle selectedTab={selectedTab} mapTitle={mapTitle} />}
      {/* Render the main layout with the Parameters section according to each input selected  */}
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
          onChangeCountry={onChangeCountry}
          onChangeExposureEconomic={onChangeExposureEconomic}
          onChangeExposureFile={onChangeExposureFile}
          onChangeExposureNonEconomic={onChangeExposureNonEconomic}
          onChangeHazard={onChangeHazard}
          onChangeHazardFile={onChangeHazardFile}
          onChangeScenario={onChangeScenario}
          onChangeTimeHorizon={onChangeTimeHorizon}
          onChangeAnnualGrowth={onChangeAnnualGrowth}
          onChangeValidEconomicExposure={onChangeValidEconomicExposure}
          onChangeValidNonEconomicExposure={onChangeValidNonEconomicExposure}
          onChangeValidHazard={onChangeValidHazard}
        />
      )}
      {/* Render the main layout with the Economic & Non-Economic section according to each sub tab selected  */}
      {/* Render Economic & non-Economic - Risk view */}
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
      {/* Render Economic & non-Economic - Adaptation view */}
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
          <PageUnderConstructionView />
        </>
      )}
    </>
  );
};

MainView.propTypes = {
  activeMap: PropTypes.string.isRequired,
  mapTitle: PropTypes.string.isRequired,
  selectedAnnualGrowth: PropTypes.number.isRequired,
  selectedAppOption: PropTypes.string.isRequired,
  selectedCard: PropTypes.string.isRequired,
  selectedCountry: PropTypes.string.isRequired,
  selectedExposureEconomic: PropTypes.string.isRequired,
  selectedExposureFile: PropTypes.string.isRequired,
  selectedExposureNonEconomic: PropTypes.string.isRequired,
  selectedHazard: PropTypes.string.isRequired,
  selectedHazardFile: PropTypes.string.isRequired,
  selectedScenario: PropTypes.string.isRequired,
  selectedSubTab: PropTypes.number.isRequired,
  selectedTab: PropTypes.number.isRequired,
  selectedTimeHorizon: PropTypes.array.isRequired,
  onChangeCountry: PropTypes.func.isRequired,
  onChangeExposureEconomic: PropTypes.func.isRequired,
  onChangeExposureFile: PropTypes.func.isRequired,
  onChangeExposureNonEconomic: PropTypes.func.isRequired,
  onChangeHazard: PropTypes.func.isRequired,
  onChangeHazardFile: PropTypes.func.isRequired,
  onChangeScenario: PropTypes.func.isRequired,
  onChangeTimeHorizon: PropTypes.func.isRequired,
  onChangeAnnualGrowth: PropTypes.func.isRequired,
  onChangeValidEconomicExposure: PropTypes.func.isRequired,
  onChangeValidNonEconomicExposure: PropTypes.func.isRequired,
  onChangeValidHazard: PropTypes.func.isRequired,
};

export default MainView;
