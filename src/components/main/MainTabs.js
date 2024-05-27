import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";

import { AppBar, Tabs, Tab, Box, Paper } from "@mui/material";

import ContentPasteIcon from "@mui/icons-material/ContentPaste";
import MacroIcon from "@mui/icons-material/Assessment";
import PaymentsIcon from "@mui/icons-material/Payments";
import TuneIcon from "@mui/icons-material/Tune";

const MainTabs = ({ onChangeTab, onChangeSubTab, propSelectedTab, propSelectedSubTab }) => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [selectedSubTab, setSelectedSubTab] = useState(0);

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
    setSelectedSubTab(0);
    onChangeTab(newValue);
  };

  const handleSubTabChange = (event, newValue) => {
    setSelectedSubTab(newValue);
    onChangeSubTab(newValue);
  };

  const subTabsMap = {
    0: [],
    1: ["Risk", "Adaptation", "+ Add to Output"], // Subtabs for "Economic & Non-Economic"
    2: ["Risk", "Adaptation"],
    3: [],
  };

  const renderSubTabs = () => {
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
          {subTabs.map((label, index) => (
            <Tab key={index} label={label} sx={{ minHeight: 24 }} /> // Apply the reduced height here as well
          ))}
        </Tabs>
      </Paper>
    );
  };

  useEffect(() => {
    setSelectedTab(propSelectedTab);
  }, [propSelectedTab]);

  return (
    <Box sx={{ flexGrow: 1, bgcolor: "#70ADB5" }}>
      <AppBar
        position="fixed"
        sx={{ bgcolor: "#70ADB5", top: "80px", zIndex: (theme) => theme.zIndex.drawer + 1 }}
      >
        <Tabs
          value={selectedTab}
          onChange={handleTabChange}
          aria-label="main navigation tabs"
          textColor="inherit"
          indicatorColor="secondary"
          centered // Center the tabs within the AppBar
          sx={{
            ".Mui-selected": { bgcolor: "#3B919D", color: "#fff" },
            ".MuiTab-root": { color: "#fff" }, // Text color for all main tabs
          }}
        >
          <Tab
            icon={<TuneIcon sx={{ fontSize: "1rem" }} />}
            iconPosition="start"
            label="Parameters"
            sx={{ display: "flex", alignItems: "center", minHeight: 48 }}
          />
          <Tab
            icon={<PaymentsIcon />}
            iconPosition="start"
            label="Economic & Non-Economic"
            sx={{ display: "flex", alignItems: "center", minHeight: 48 }}
          />
          <Tab
            icon={<MacroIcon />}
            iconPosition="start"
            label="Macroeconomic (In Dev.)"
            sx={{ display: "flex", alignItems: "center", minHeight: 48 }}
          />
          <Tab
            icon={<ContentPasteIcon />}
            iconPosition="start"
            label="Outputs (Reporting)"
            sx={{ display: "flex", alignItems: "center", minHeight: 48 }}
          />
        </Tabs>
      </AppBar>
      {renderSubTabs()}
    </Box>
  );
};

MainTabs.propTypes = {
  onChangeTab: PropTypes.func.isRequired,
  onChangeSubTab: PropTypes.func.isRequired,
  propSelectedSubTab: PropTypes.number.isRequired,
  propSelectedTab: PropTypes.number.isRequired,
};

export default MainTabs;
