import React from "react";

import { AppBar, Box, Tabs, Tab } from "@mui/material";
import ContentPasteIcon from "@mui/icons-material/ContentPaste";
import MacroIcon from "@mui/icons-material/Assessment";
import PaymentsIcon from "@mui/icons-material/Payments";
import TuneIcon from "@mui/icons-material/Tune";

import { useReportTools } from "../../utils/reportTools";
import MainSubTabs from "./MainSubTabs";
import useStore from "../../store";

const MainTabs = () => {
  const { selectedAppOption, selectedTab, setSelectedTab, setSelectedSubTab } = useStore();
  const { fetchReports } = useReportTools();

  const onFetchReportsHandler = async () => {
    await fetchReports();
  };

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
    if (newValue === 3) {
      onFetchReportsHandler();
    }
    setSelectedSubTab(0);
  };

  return (
    <Box sx={{ bgcolor: "#70ADB5" }}>
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
            label="Macroeconomic"
            sx={{ display: "flex", alignItems: "center", minHeight: 48 }}
            disabled={selectedAppOption === "explore"}
          />
          <Tab
            icon={<ContentPasteIcon />}
            iconPosition="start"
            label="Outputs (Reporting)"
            sx={{ display: "flex", alignItems: "center", minHeight: 48 }}
          />
        </Tabs>
      </AppBar>
      <MainSubTabs />
    </Box>
  );
};

export default MainTabs;
