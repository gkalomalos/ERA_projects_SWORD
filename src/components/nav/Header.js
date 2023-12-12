import * as React from "react";
import { useTranslation } from "react-i18next";

import AppBar from "@mui/material/AppBar";
import IconButton from "@mui/material/IconButton";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";

import SettingsIcon from "@mui/icons-material/Settings";

import LanguageSelector from "./LanguageSelector";
import SettingsModal from "./SettingsModal";
import ShutdownButton from "./ShutdownButton";

import climada_logo from "../../assets/climada_logo.png";
import css from "./Header.module.css";

const Header = () => {
  const { t } = useTranslation();
  const settingsModalRef = React.useRef();

  const handleOpenSettings = () => {
    if (settingsModalRef.current) {
      settingsModalRef.current.openModal();
    }
  };

  return (
    <AppBar position="static" sx={{ bgcolor: "#2A4D69" }}>
      <Toolbar
        disableGutters
        sx={{ width: "100%", display: "flex", justifyContent: "space-between" }}
      >
        <div style={{ flex: 1 }}>
          <img src={climada_logo} alt="climada_logo" className={css.logo_climada} />
        </div>
        <div style={{ flex: 1, display: "flex", justifyContent: "center" }}>
          <Typography
            variant="h3"
            fontFamily={[
              '"FFKievitStdBook"',
              "Calibri",
              "-apple-system",
              "BlinkMacSystemFont",
              '"Segoe UI"',
              "Roboto",
              '"Helvetica Neue"',
              "Arial",
              '"Noto Sans"',
              "sans-serif",
              '"Apple Color Emoji"',
              '"Segoe UI Emoji"',
              '"Segoe UI Symbol"',
              '"Noto Color Emoji"',
            ].join(",")}
            noWrap
            component="div"
            sx={{ m: 1.5, display: { xs: "none", md: "flex" } }}
          >
            {t("application_title")}
          </Typography>
        </div>
        <div style={{ flex: 1, display: "flex", justifyContent: "flex-end" }}>
          <LanguageSelector />
          <IconButton color="inherit" onClick={handleOpenSettings}>
            <SettingsIcon />
          </IconButton>
          <SettingsModal ref={settingsModalRef} />
          <ShutdownButton />
        </div>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
