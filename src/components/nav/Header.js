import * as React from "react";
import { useTranslation } from "react-i18next";

import AppBar from "@mui/material/AppBar";
import IconButton from "@mui/material/IconButton";
import LanguageIcon from "@mui/icons-material/Language";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";

import SettingsIcon from "@mui/icons-material/Settings";

import SettingsModal from "./SettingsModal";
import LoadModal from "./LoadModal";

import climada_logo from "../../assets/climada_logo.png";
import css from "./Header.module.css";

const Header = () => {
  const { t, i18n } = useTranslation();
  const [anchorEl, setAnchorEl] = React.useState(null);
  const [isSettingsModalOpen, setSettingsModalOpen] = React.useState(false);

  const languages = [
    { code: "en", label: t("language_en"), short: t("language_en_short") },
    { code: "ar", label: t("language_ar"), short: t("language_ar_short") },
    { code: "th", label: t("language_th"), short: t("language_th_short") },
  ];

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLanguageChange = (langCode) => {
    i18n.changeLanguage(langCode);
    setAnchorEl(null);
  };

  const handleOpenSettings = () => {
    setSettingsModalOpen(true);
  };

  const handleCloseSettings = () => {
    setSettingsModalOpen(false);
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
          {" "}
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
          <IconButton color="inherit" onClick={(e) => setAnchorEl(e.currentTarget)}>
            <LanguageIcon />
          </IconButton>
          <IconButton color="inherit" onClick={handleOpenSettings}>
            <SettingsIcon />
          </IconButton>
          <SettingsModal
            isSettingsModalOpen={isSettingsModalOpen}
            handleCloseSettings={handleCloseSettings}
          />
          <Menu
            id="language-menu"
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleClose}
          >
            {languages.map((lang) => (
              <MenuItem
                key={lang.code}
                selected={i18n.language === lang.code}
                onClick={() => handleLanguageChange(lang.code)}
              >
                {lang.label}
              </MenuItem>
            ))}
          </Menu>
        </div>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
