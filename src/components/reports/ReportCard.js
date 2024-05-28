/* eslint-disable no-unused-vars */
import React, { useState } from "react";
import { useTranslation } from "react-i18next";
import image from "./risks_waterfall_plot.png";

import { Box, Typography, IconButton, List, ListItem, ListItemText } from "@mui/material";
import { Delete, ArrowUpward, ArrowDownward } from "@mui/icons-material";

import AlertMessage from "../alerts/AlertMessage";

const ReportsCard = () => {
  const { t } = useTranslation();

  const [message, setMessage] = useState("");
  const [severity, setSeverity] = useState("info");
  const [showMessage, setShowMessage] = useState(true);

  const handleCloseMessage = () => {
    setShowMessage(false);
  };

  const handleDeleteButtonClick = () => {
    console.log("delete");
  };

  const handleDownButtonClick = () => {
    console.log("up");
  };

  const handleUpButtonClick = () => {
    console.log("down");
  };

  return (
    <Box
      sx={{
        alignItems: "flex-start",
        border: "1px solid #ccc",
        borderRadius: "16px",
        display: "flex",
        flexDirection: "row",
        marginBottom: 2,
        width: "100%",
        // maxHeight: "128px",
        height: "128px",
      }}
    >
      <Box sx={{ flex: 1, maxWidth: "10%" }}>
        <List dense>
          <ListItem>
            <ListItemText primary="Title:" />
          </ListItem>
          <ListItem>
            <ListItemText secondary="Type:" />
          </ListItem>
          <ListItem>
            <ListItemText secondary="Data:" />
          </ListItem>
        </List>
      </Box>

      <Box sx={{ flex: 2, maxWidth: "55%" }}>
        <List dense>
          <ListItem>
            <ListItemText primary="Flood Expansion – return period 1 in 100 years" />
          </ListItem>
          <ListItem>
            <ListItemText secondary="Economic – Risk – Hazard – Map" />
          </ListItem>
          <ListItem>
            <ListItemText secondary="Thailand/2050/SSP2-4.5/Flood/Markets/GDP2/..." />
          </ListItem>
        </List>
      </Box>

      <Box
        component="img"
        sx={{
          flex: 1,
          maxWidth: "25%",
          width: "128px",
          height: "128px",
          marginBottom: 2,
        }}
        alt="Map"
        src={image}
      />

      <Box>
        <Box sx={{ display: "flex", flexDirection: "column", alignItems: "start", width: "100%" }}>
          <IconButton onClick={handleDeleteButtonClick} sx={{ marginBottom: 1 }}>
            <Delete />
            <Typography>Remove</Typography>
          </IconButton>
          <IconButton onClick={handleUpButtonClick} sx={{ marginBottom: 1 }}>
            <ArrowUpward />
            <Typography>Move Up</Typography>
          </IconButton>
          <IconButton onClick={handleDownButtonClick}>
            <ArrowDownward />
            <Typography>Move Down</Typography>
          </IconButton>
        </Box>
      </Box>
    </Box>
  );
};

export default ReportsCard;
