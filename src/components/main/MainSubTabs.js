import React from "react";

import { Box, Button, Tabs, Tab, Paper } from "@mui/material";

import useStore from "../../store";
import AlertMessage from "../alerts/AlertMessage";
import { useMapTools } from "../../utils/mapTools";

const MainSubTabs = () => {
  const { selectedSubTab, selectedTab, setSelectedSubTab } = useStore();
  const { handleSaveMap, handleAddToOutput } = useMapTools();

  const subTabsMap = {
    0: [], // Subtabs for "Parameters section"
    1: ["Risk", "Adaptation", "+ Add to Output", "+ Save Map"], // Added "Save to Map" button
    2: ["Risk", "Adaptation"], // Subtabs for "Macroeconomic (in dev) section"
    3: [], // Subtabs for "Outputs (reporting) section"
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
          // Conditionally render a button instead of a tab for "+ Add to Output" and "Save to Map"
          index === 2 || index === 3 ? (
            <Box
              key={index}
              sx={{ position: "absolute", top: 0, right: index === 2 ? 100 : index === 3 ? 0 : 8 }}
            >
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
                onClick={index === 2 ? handleAddToOutput : handleSaveMap}
              >
                {label}
              </Button>
            </Box>
          ) : (
            <Tab key={index} label={label} sx={{ minHeight: 24 }} /> // Apply the reduced height
          )
        )}
      </Tabs>
      <AlertMessage />
    </Paper>
  );
};

export default MainSubTabs;
