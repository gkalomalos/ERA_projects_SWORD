import React from "react";

import { Box, Grid } from "@mui/material";

import AlertMessage from "../alerts/AlertMessage";
import Country from "./Country";
import MacroEconomicViewTitle from "../title/MacroEconomicViewTitle";
import Sector from "./Sector";
import Hazard from "./Hazard";
import MacroEconomicVariable from "./MacroEconomicVariable";
import Scenario from "./Scenario";
import useStore from "../../store";
import PlotMacroButton from "../nav/RunPlotMacroButton";

const MacroEconomicInput = () => {
  const { selectedTab } = useStore();

  if (!(selectedTab === 2)) {
    return null;
  }

  return (
    <>
      {/* MacroEconomic title section */}
      <MacroEconomicViewTitle />

      {/* DataInput parameters section */}
      <Box sx={{ backgroundColor: "#DDEBEF", padding: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Country />
          </Grid>
          <Grid item xs={12}>
            <Hazard />
          </Grid>
          <Grid item xs={12}>
            <Scenario />
          </Grid>
          <Grid item xs={12}>
            <Sector />
          </Grid>
          <Grid item xs={12}>
            <MacroEconomicVariable />
          </Grid>
        </Grid>

        {/* Run button section */}
        <Grid item xs={12}>
          <PlotMacroButton />
        </Grid>

        {/* Alert message section */}
        <AlertMessage />
      </Box>
    </>
  );
};

export default MacroEconomicInput;
