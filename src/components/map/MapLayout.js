import React from "react";
import PropTypes from "prop-types";

import { Paper } from "@mui/material";

import ExposureMap from "./ExposureMap";
import HazardMap from "./HazardMap";
import RiskMap from "./RiskMap";

const MapLayout = ({ activeMap, selectedCountry }) => {
  return (
    <div style={{ height: "80%", display: "flex", flexDirection: "column" }}>
      <Paper
        elevation={3}
        style={{
          flex: 1,
          borderRadius: "15px",
          marginBottom: "16px",
          overflow: "hidden",
        }}
      >
        {activeMap === "exposure" && <ExposureMap selectedCountry={selectedCountry} />}
        {activeMap === "hazard" && <HazardMap selectedCountry={selectedCountry} />}
        {activeMap === "impact" && <RiskMap selectedCountry={selectedCountry} />}
      </Paper>
    </div>
  );
};

MapLayout.propTypes = {
  activeMap: PropTypes.string.isRequired,
  selectedCountry: PropTypes.string.isRequired,
};

export default MapLayout;
