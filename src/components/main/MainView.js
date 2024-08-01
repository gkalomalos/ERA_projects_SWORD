import React from "react";

import AdaptationMap from "../map/AdaptationMap";
import AdaptationChartLayout from "../controls/AdaptationChartLayout";
import RiskChartLayout from "../controls/RiskChartLayout";
import MacroEconomicView from "../main/MacroEconomicView";
import MainViewControls from "../controls/MainViewControls";
import MainViewTitle from "../title/MainViewTitle";
import MapLayout from "../map/MapLayout";
import ProgressView from "../controls/ProgressView";
import SettingsView from "../controls/SettingsView";
import ViewCard from "../cards/ViewCard";
import ReportsView from "../reports/ReportsView";
import useStore from "../../store";

const MainView = () => {
  const { selectedSubTab, selectedTab, viewControl } = useStore();

  return (
    <>
      {<MainViewTitle />}
      {selectedTab === 0 && <ViewCard />}
      {selectedTab === 1 && selectedSubTab === 0 && (
        <>
          {viewControl === "display_map" && <MapLayout />}
          {viewControl === "display_chart" && <RiskChartLayout />}
          {viewControl === "settings" && <SettingsView />}
          {viewControl === "progress" && <ProgressView />}
          <MainViewControls />
        </>
      )}
      {selectedTab === 1 && selectedSubTab === 1 && (
        <>
          {viewControl === "display_map" && <AdaptationMap />}
          {viewControl === "display_chart" && <AdaptationChartLayout />}
          {viewControl === "settings" && <SettingsView />}
          {viewControl === "progress" && <ProgressView />}
          <MainViewControls />
        </>
      )}
      {selectedTab === 2 && (
        <>
          <MacroEconomicView />
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
