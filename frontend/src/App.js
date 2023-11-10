import React from "react";

import { Grid } from "@mui/material";

import Header from "./components/nav/Header";
import DataInput from "./components/input/DataInput";
import MapLayout from "./components/map/MapLayout";

const App = () => {
  return (
    <>
      <Header />
      <Grid
        container
        spacing={2}
        style={{ padding: "16px", height: "calc(100vh - 64px)" }}
      >
        <Grid item xs={12} md={3}>
          <DataInput />
        </Grid>
        <Grid item xs={12} md={9}>
          <MapLayout />
        </Grid>
      </Grid>
    </>
  );
};

export default App;
