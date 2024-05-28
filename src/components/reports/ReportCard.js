/* eslint-disable no-unused-vars */
import React, { useState } from "react";
import { useTranslation } from "react-i18next";

import {
  Box,
  Typography,
  IconButton,
  Icon,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from "@mui/material";
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
        border: "1px solid #ccc",
        borderRadius: "16px",
        padding: 2,
        // marginBottom: 2,
        // m:2,
        display: "flex",
        flexDirection: "column",
        alignItems: "flex-start",
        // width: 300,
      }}
    >
      <Typography variant="h6" gutterBottom>
        Flood Expansion – <span style={{ fontWeight: "normal" }}>return period 1 in 100 years</span>
      </Typography>
      <List dense>
        <ListItem>
          <ListItemText
            primary={
              <>
                <span style={{ fontWeight: "bold" }}>Type:</span> Economic – Risk – Hazard – Map
              </>
            }
          />
        </ListItem>
        <ListItem>
          <ListItemText
            primary={
              <>
                <span style={{ fontWeight: "bold" }}>Data:</span>{" "}
                Thailand/2050/SSP2-4.5/Flood/Markets/GDP2/...
              </>
            }
          />
        </ListItem>
      </List>
      <Box
        component="img"
        sx={{
          width: "100%",
          height: "auto",
          marginBottom: 2,
        }}
        alt="Map"
        src="your-image-url" // Replace this with the actual URL or import of your image
      />
      <Box
        sx={{
          display: "flex",
          justifyContent: "space-between",
          width: "100%",
        }}
      >
        <Box>
          <IconButton onClick={() => handleDeleteButtonClick()}>
            <Delete />
            <Typography>Remove</Typography>
          </IconButton>
          <IconButton onClick={() => handleUpButtonClick()}>
            <ArrowUpward />
            <Typography>Move Up</Typography>
          </IconButton>
          <IconButton onClick={() => handleDownButtonClick()}>
            <ArrowDownward />
            <Typography>Move Down</Typography>
          </IconButton>
        </Box>
      </Box>
    </Box>
  );
};
export default ReportsCard;
