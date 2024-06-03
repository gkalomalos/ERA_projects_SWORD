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
  const [viewControl, setViewControl] = useState("display_map");
  const { selectedSubTab, selectedTab } = useStore();

  const setViewControlHandler = (control) => {
    setViewControl(control);
  };

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
