import React, { useState, useEffect } from "react";

import APIService from "../../APIService";

import { Paper, Box, Button, Typography } from "@mui/material";
import PublicIcon from "@mui/icons-material/Public";
import ReportProblemIcon from "@mui/icons-material/ReportProblem";
import TimelineIcon from "@mui/icons-material/Timeline";

import Map from "./Map";

const MapLayout = () => {
  const [activeMap, setActiveMap] = useState("hazards");
  const [isExposuresSelected, setIsExposuresSelected] = useState(false);
  const [isHazardsSelected, setIsHazardsSelected] = useState(true);
  const [isRisksSelected, setIsRisksSelected] = useState(false);
  const [mapData, setMapData] = useState(null);

  const fetchMapData = async () => {
    const fetchedData = await APIService.Test();
    // Data is fetched as: fetchedData.result.data.mapTitle
    if (fetchedData && fetchedData.result.data.mapData) {
      setMapData(fetchedData.result.data.mapData);
    }
  };

  const onClickExposureButtonHandler = () => {
    fetchMapData();
    setIsExposuresSelected(true);
    setIsHazardsSelected(false);
    setIsRisksSelected(false);
    setActiveMap("exposures");
  };

  const onClickHazardButtonHandler = () => {
    setIsExposuresSelected(false);
    setIsHazardsSelected(true);
    setIsRisksSelected(false);
    setActiveMap("hazards");
  };

  const onClickRiskButtonHandler = () => {
    setIsExposuresSelected(false);
    setIsHazardsSelected(false);
    setIsRisksSelected(true);
    setActiveMap("risks");
  };

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <Paper
        elevation={3}
        style={{
          flex: 1,
          borderRadius: "15px",
          marginBottom: "16px",
          overflow: "hidden",
        }}
      >
        <Map mapData={mapData} />
      </Paper>
      <Box sx={{ textAlign: "center", marginBottom: 4 }}>
        <Button
          onClick={onClickExposureButtonHandler}
          size="medium"
          startIcon={<PublicIcon />}
          sx={{
            marginRight: 4,
            minWidth: "120px",
            maxWidth: "120px",
            bgcolor: isExposuresSelected ? "#2A4D69" : "#5C87B1",
            "&:hover": { bgcolor: "9886D6" },
          }}
          variant="contained"
        >
          Exposure
        </Button>
        <Button
          onClick={onClickHazardButtonHandler}
          size="medium"
          startIcon={<ReportProblemIcon />}
          sx={{
            marginRight: 4,
            minWidth: "120px",
            maxWidth: "120px",
            bgcolor: isHazardsSelected ? "#2A4D69" : "#5C87B1",
            "&:hover": { bgcolor: "9886D6" },
          }}
          variant="contained"
        >
          Hazard
        </Button>
        <Button
          onClick={onClickRiskButtonHandler}
          size="medium"
          startIcon={<TimelineIcon />}
          sx={{
            minWidth: "120px",
            maxWidth: "120px",
            bgcolor: isRisksSelected ? "#2A4D69" : "#5C87B1",
            "&:hover": { bgcolor: "9886D6" },
          }}
          variant="contained"
        >
          Risk
        </Button>
      </Box>
    </div>
  );
};

export default MapLayout;
