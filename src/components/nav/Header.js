import * as React from "react";

import AppBar from "@mui/material/AppBar";
import IconButton from "@mui/material/IconButton";
import LanguageIcon from "@mui/icons-material/Language";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";

import climada_logo from "../../assets/climada_logo.png";
import css from "./Header.module.css";

const Header = () => {
  const [language, setLanguage] = React.useState("EN");
  const [anchorEl, setAnchorEl] = React.useState(null);

  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <AppBar position="static" sx={{ bgcolor: "#2A4D69" }}>
      <Toolbar
        disableGutters
        sx={{ width: "100%", display: "flex", justifyContent: "space-between" }}
      >
        <img src={climada_logo} alt="climada_logo" className={css.logo_climada} />
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
          CLIMADA UNU
        </Typography>
        <IconButton color="inherit" onClick={(e) => setAnchorEl(e.currentTarget)}>
          <LanguageIcon />
        </IconButton>
        <Menu id="language-menu" anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleClose}>
          {["EN", "AR", "TH"].map((lang) => (
            <MenuItem
              key={lang}
              selected={lang === language}
              onClick={() => {
                setLanguage(lang);
                handleClose();
              }}
            >
              {lang === "EN" ? "English" : lang === "AR" ? "Arabic" : "Thai"}
            </MenuItem>
          ))}
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
