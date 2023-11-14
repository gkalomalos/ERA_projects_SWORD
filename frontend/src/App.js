import React, { useState, useEffect } from "react";

import { Grid } from "@mui/material";

import Header from "./components/nav/Header";
import DataInput from "./components/input/DataInput";
import MapLayout from "./components/map/MapLayout";
import LoadModal from "./components/nav/LoadModal";

const App = () => {
  const [isScenarioRunning, setIsScenarioRunning] = useState(false);
  const [modalMessage, setModalMessage] = useState("");

  const setIsScenarioRunningHandler = (data) => {
    setIsScenarioRunning(data);
  };

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
      <Header />
      <Grid
        container
        spacing={2}
        style={{ padding: "16px", height: "calc(100vh - 64px)" }}
      >
        <Grid item xs={12} md={3}>
          <DataInput onScenarioRunning={setIsScenarioRunningHandler} />
        </Grid>
        <Grid item xs={12} md={9}>
          <MapLayout />
        </Grid>
      </Grid>
      {isScenarioRunning && (
        <LoadModal message={modalMessage} open={isScenarioRunning} />
      )}
    </>
  );
};

export default App;
