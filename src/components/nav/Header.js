import * as React from "react";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Typography from "@mui/material/Typography";
import Grid from "@mui/material/Grid";

import css from "./Header.module.css";
import climada_logo from "../../assets/climada_logo.png";

const Header = () => {
  return (
    <AppBar position="static" sx={{ bgcolor: "#2A4D69" }}>
      <Grid container spacing={1}>
        <Grid item xs={5}>
          <img
            src={climada_logo}
            alt="climada_logo"
            className={css.logo_climada}
          />
        </Grid>
        <Grid item xs={6}>
          <Toolbar disableGutters>
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
          </Toolbar>
        </Grid>
      </Grid>
    </AppBar>
  );
};
export default Header;
