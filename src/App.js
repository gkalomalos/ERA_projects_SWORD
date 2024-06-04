import React from "react";

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
  const { selectedAppOption, selectedTab, selectedSubTab } = useStore();

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
                <ResultsView />
              </Grid>
            )}
          </Grid>
          <LoadModal />
        </>
      )}
    </>
  );
};

export default App;
