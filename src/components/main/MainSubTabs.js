import React from "react";

import { Box, Button, Tabs, Tab, Paper } from "@mui/material";

import useStore from "../../store";

import image1 from "../../assets/hazard_map_1.png";
// import image2 from "./risks_waterfall_plot_1.png";

const MainSubTabs = () => {
  const {
    addReport,
    isScenarioRunCompleted,
    // selectedAnnualGrowth,
    // selectedAppOption,
    selectedCountry,
    selectedExposureEconomic,
    selectedExposureNonEconomic,
    selectedHazard,
    selectedScenario,
    selectedTimeHorizon,
    selectedSubTab,
    selectedTab,
    setSelectedSubTab,
  } = useStore();
  const subTabsMap = {
    0: [], // Subtabs for "Parameters section"
    1: ["Risk", "Adaptation", "+ Add to Output"], // Subtabs for "Economic & Non-Economic section"
    2: ["Risk", "Adaptation"], // Subtabs for "Macroeconomic (in dev) section"
    3: [], // Subtabs for "Outputs (reporting) section"
  };

  const handleAddToOutput = () => {
    if (isScenarioRunCompleted) {
      const outputData = {
        id: new Date().getTime().toString(),
        // data: JSON.stringify({
        //   selectedAnnualGrowth: selectedAnnualGrowth,
        //   selectedAppOption: selectedAppOption,
        //   selectedCountry: selectedCountry,
        //   selectedExposureEconomic: selectedExposureEconomic,
        //   selectedExposureNonEconomic: selectedExposureNonEconomic,
        //   selectedHazard: selectedHazard,
        //   selectedScenario: selectedScenario,
        //   selectedTimeHorizon: selectedTimeHorizon,
        // }),
        data: `${selectedCountry} - ${selectedHazard} - ${selectedScenario} - ${
          selectedExposureEconomic ? selectedExposureEconomic : selectedExposureNonEconomic
        } - ${selectedTimeHorizon}`,
        image: image1,
        title: `Impact of ${selectedHazard} on ${
          selectedExposureEconomic ? selectedExposureEconomic : selectedExposureNonEconomic
        }`,
        type: "outputData",
      };
      addReport(outputData);
    }
  };

  const handleSubTabChange = (event, newValue) => {
    setSelectedSubTab(newValue);
  };

  const subTabs = subTabsMap[selectedTab];
  if (!subTabs) {
    return null; // This main tab does not have subtabs
  }

  return (
    <Paper
      square
      sx={{
        position: "fixed",
        top: "128px",
        zIndex: (theme) => theme.zIndex.drawer + 1,
        width: "100%",
        bgcolor: "#8AC8D0",
      }}
    >
      <Tabs
        value={selectedSubTab}
        onChange={handleSubTabChange}
        aria-label={`sub navigation tabs for main tab ${selectedTab}`}
        textColor="inherit"
        indicatorColor="secondary"
        variant="fullWidth"
        centered
        sx={{
          minHeight: 24,
          ".Mui-selected": { bgcolor: "#45ABB9", color: "#fff" },
          ".MuiTab-root": {
            color: "#fff",
            fontSize: "0.875rem", // Smaller text
            minHeight: 24, // Reduce the height of the tabs
            padding: "6px 12px", // Reduce the padding around the text
          },
          ".MuiTabs-indicator": {
            height: 2, // Smaller indicator height
          },
          ".MuiTab-root:not(.Mui-selected)": { bgcolor: "#8AC8D0" },
        }}
      >
        {subTabs.map((label, index) =>
          // Conditionally render a button instead of a tab for "+ Add to Output"
          index === 2 ? (
            <Box key={index} sx={{ position: "absolute", top: 0, right: 8 }}>
              <Button
                variant="contained"
                size="small"
                sx={{
                  bgcolor: "#FFCCCC",
                  transition: "transform 0.1s ease-in-out",
                  "&:active": {
                    transform: "scale(0.96)",
                  },
                  "&:hover": { bgcolor: "#F79191" },
                  textTransform: "none",
                }}
                onClick={() => handleAddToOutput()}
              >
                {label}
              </Button>
            </Box>
          ) : (
            <Tab key={index} label={label} sx={{ minHeight: 24 }} /> // Apply the reduced height
          )
        )}
      </Tabs>
    </Paper>
  );
};

export default MainSubTabs;
