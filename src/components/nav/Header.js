import * as React from "react";

import AppBar from "@mui/material/AppBar";
import Grid from "@mui/material/Grid";
import MenuItem from "@mui/material/MenuItem";
import Select from "@mui/material/Select";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";

import climada_logo from "../../assets/climada_logo.png";
import css from "./Header.module.css";

const Header = () => {
  const [language, setLanguage] = React.useState("EN");

  const handleLanguageChange = (event) => {
    setLanguage(event.target.value);
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
        <Select
          value={language}
          onChange={handleLanguageChange}
          displayEmpty
          inputProps={{ "aria-label": "Without label" }}
          sx={{ m: 1, color: "white", width: 120 }}
        >
          <MenuItem value="EN">English</MenuItem>
          <MenuItem value="AR">Arabic</MenuItem>
          <MenuItem value="TH">Thai</MenuItem>
        </Select>
      </Toolbar>
    </AppBar>
  );
};

export default Header;
