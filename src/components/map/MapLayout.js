import React, { useState } from "react";

import { Paper, Box, Button, Typography } from "@mui/material";
import AttachMoneyIcon from "@mui/icons-material/AttachMoney";
import PublicIcon from "@mui/icons-material/Public";
import ReportProblemIcon from "@mui/icons-material/ReportProblem";
import TimelineIcon from "@mui/icons-material/Timeline";

import Map from "./Map";
import HazardMap from "./HazardMap";

const MapLayout = (props) => {
  const [activeMap, setActiveMap] = useState("exposures");
  const [isExposuresSelected, setIsExposuresSelected] = useState(true);
  const [isHazardsSelected, setIsHazardsSelected] = useState(false);
  const [isRisksSelected, setIsRisksSelected] = useState(false);
  const [isCostsSelected, setIsCostsSelected] = useState(false);

  const onClickExposureButtonHandler = () => {
    setIsExposuresSelected(true);
    setIsHazardsSelected(false);
    setIsRisksSelected(false);
    setIsCostsSelected(false);
    setActiveMap("exposures");
  };

  const onClickHazardButtonHandler = () => {
    setIsExposuresSelected(false);
    setIsHazardsSelected(true);
    setIsRisksSelected(false);
    setIsCostsSelected(false);
    setActiveMap("hazards");
  };

  const onClickRiskButtonHandler = () => {
    setIsExposuresSelected(false);
    setIsHazardsSelected(false);
    setIsRisksSelected(true);
    setIsCostsSelected(false);
    setActiveMap("risks");
  };

  const onClickCostButtonHandler = () => {
    setIsExposuresSelected(false);
    setIsHazardsSelected(false);
    setIsRisksSelected(false);
    setIsCostsSelected(true);
    setActiveMap("costs");
  };

  return (
    <div style={{ height: "100%", display: "flex", flexDirection: "column" }}>
      <Typography
        id="map-title"
        gutterBottom
        variant="h6"
        sx={{ fontWeight: "bold", marginTop: 4 }}
        textAlign="center"
      >
        {props.mapTitle}
      </Typography>
      <Paper
        elevation={3}
        style={{
          flex: 1,
          borderRadius: "15px",
          marginBottom: "16px",
          overflow: "hidden",
        }}
      >
        <HazardMap activeMap={activeMap} selectedCountry={props.selectedCountry} />
      </Paper>
      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          flexWrap: "wrap",
          textAlign: "center",
          marginBottom: 4,
        }}
      >
        <Button
          onClick={onClickExposureButtonHandler}
          size="medium"
          startIcon={<PublicIcon />}
          sx={{
            flexGrow: 1,
            margin: 1,
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
            flexGrow: 1,
            margin: 1,
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
            flexGrow: 1,
            margin: 1,
            marginRight: 4,
            minWidth: "120px",
            maxWidth: "120px",
            bgcolor: isRisksSelected ? "#2A4D69" : "#5C87B1",
            "&:hover": { bgcolor: "9886D6" },
          }}
          variant="contained"
        >
          Impact
        </Button>
        <Button
          onClick={onClickCostButtonHandler}
          size="medium"
          startIcon={<AttachMoneyIcon />}
          sx={{
            flexGrow: 1,
            margin: 1,
            minWidth: "120px",
            maxWidth: "120px",
            bgcolor: isCostsSelected ? "#2A4D69" : "#5C87B1",
            "&:hover": { bgcolor: "9886D6" },
          }}
          variant="contained"
        >
          Cost
        </Button>
      </Box>
    </div>
  );
};

export default MapLayout;
