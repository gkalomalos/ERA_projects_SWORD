import React, { useState, useEffect } from "react";

import { Paper, Box, Button, Typography } from "@mui/material";
import PublicIcon from "@mui/icons-material/Public";
import ReportProblemIcon from "@mui/icons-material/ReportProblem";
import TimelineIcon from "@mui/icons-material/Timeline";

import Map from "./Map";

const MapLayout = () => {
  const [activeMap, setActiveMap] = useState("exposures");
  const [isExposuresSelected, setIsExposuresSelected] = useState(true);
  const [isHazardsSelected, setIsHazardsSelected] = useState(false);
  const [isRisksSelected, setIsRisksSelected] = useState(false);

  const onClickExposureButtonHandler = () => {
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
        <Map />
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
