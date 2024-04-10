import React, { useState } from "react";
import { useTranslation } from "react-i18next";

import { AppBar, Toolbar, IconButton, Typography } from "@mui/material";
import SettingsIcon from "@mui/icons-material/Settings";

import HelpButton from "./HelpButton";
import LanguageSelector from "./LanguageButton";
import MinimizeButton from "./MinimizeButton";
import ReloadButton from "./ReloadButton";
import SettingsModal from "./SettingsButton";
import ShutdownButton from "./ShutdownButton";

import giz_logo from "../../assets/giz_logo.png";
import unu_ehs_logo from "../../assets/unu_ehs_logo.png";
import css from "./Header.module.css";

const Header = () => {
  const { t } = useTranslation();
  const [isSettingsModalOpen, setSettingsModalOpen] = useState(false);

  const handleOpenSettings = () => {
    setSettingsModalOpen(true);
  };

  const handleCloseSettings = () => {
    setSettingsModalOpen(false);
  };

  return (
    <AppBar
      position="fixed"
      sx={{ bgcolor: "#8fc3d1", top: 0, zIndex: (theme) => theme.zIndex.drawer + 1 }}
    >
      <Toolbar
        disableGutters
        sx={{
          width: "100%",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center", // Ensure items are aligned in the center vertically
          flexWrap: "nowrap", // Prevent wrapping of items
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center", // Align logos in the center vertically
            justifyContent: "flex-start", // Align logos to the start horizontally
            overflow: "hidden", // Prevent overflow
          }}
        >
          <img src={giz_logo} alt="giz_logo" className={css.logo_giz} />
          <img src={unu_ehs_logo} alt="unu_ehs_logo" className={css.logo_unu} />
        </div>
        <Typography
          variant="h3"
          noWrap
          component="div"
          sx={{
            flexGrow: 1,
            textAlign: "center", // Center the title text
            m: 1.5,
            display: { xs: "none", sm: "block" }, // Hide on extra small screens if necessary
          }}
        >
          {t("application_title")}
        </Typography>
        <div style={{ display: "flex", alignItems: "center" }}>
          <ReloadButton />
          <LanguageSelector />
          <IconButton color="inherit" onClick={handleOpenSettings}>
            <SettingsIcon />
          </IconButton>
          <SettingsModal isOpen={isSettingsModalOpen} onClose={handleCloseSettings} />
          <HelpButton />
          <MinimizeButton />
          <ShutdownButton />
        </div>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
