import React, { useState } from "react";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";

import { Box, Typography, IconButton, List, ListItem, ListItemText } from "@mui/material";
import { Delete, ArrowUpward, ArrowDownward } from "@mui/icons-material";

import AlertMessage from "../alerts/AlertMessage";
import useStore from "../../store";

const ReportsCard = ({ data, image, id, isSelected, onCardClick, onReportAction, title, type }) => {
  const { t } = useTranslation();
  const { setAlertMessage, setAlertSeverity, setAlertShowMessage } = useStore();

  const [clicked, setClicked] = useState(false); // State to manage click animation

  const handleMouseDown = () => {
    setClicked(true); // Trigger animation
  };

  const handleMouseUp = () => {
    setClicked(false); // Reset animation
  };

  const handleClick = () => {
    onCardClick(id);
  };

  const handleDeleteButtonClick = () => {
    setAlertMessage("Report deleted successfully.");
    setAlertSeverity("success");
    setAlertShowMessage(true);
    onReportAction(id, "delete");
  };

  const handleDownButtonClick = () => {
    onReportAction(id, "down");
  };

  const handleUpButtonClick = () => {
    onReportAction(id, "up");
  };

  return (
    <>
      <Box
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp} // Reset animation when the mouse leaves the card
        onClick={handleClick}
        sx={{
          alignItems: "flex-start",
          backgroundColor: isSelected ? "#EBF3F5" : "FFFFFF",
          border: "1px solid #ccc",
          borderRadius: "16px",
          display: "flex",
          flexDirection: "row",
          marginBottom: 2,
          width: "100%",

          cursor: "pointer",
          transition: "background-color 0.3s, transform 0.1s", // Added transform to the transition
          "&:hover": {
            bgcolor: "#DAE7EA",
          },
          ".MuiCardContent-root:last-child": {
            padding: 2,
          },
          transform: clicked ? "scale(0.97)" : "scale(1)", // Apply scale transform when clicked
        }}
      >
        <Box sx={{ flex: 1, maxWidth: "10%" }}>
          <List dense disablePadding>
            <ListItem>
              <ListItemText
                primary={<Typography variant="body2">{t("results_report_card_title")}</Typography>}
              />
            </ListItem>
            <ListItem>
              <ListItemText
                secondary={<Typography variant="body2">{t("results_report_card_type")}</Typography>}
              />
            </ListItem>
            <ListItem>
              <ListItemText
                secondary={<Typography variant="body2">{t("results_report_card_data")}</Typography>}
              />
            </ListItem>
          </List>
        </Box>

        <Box sx={{ flex: 2, maxWidth: "55%" }}>
          <List dense disablePadding>
            <ListItem>
              <ListItemText primary={title} />
            </ListItem>
            <ListItem>
              <ListItemText secondary={type} />
            </ListItem>
            <ListItem>
              <ListItemText secondary={data} />
            </ListItem>
          </List>
        </Box>

        <Box sx={{ flex: 3, maxWidth: "25%" }}>
          <Box
            component="img"
            sx={{
              width: "128px",
              height: "100%",
            }}
            alt="report_image"
            src={image}
          />
        </Box>

        <Box>
          <Box
            sx={{ display: "flex", flexDirection: "column", alignItems: "start", width: "100%" }}
          >
            <IconButton aria-label="delete" onClick={handleDeleteButtonClick} size="small">
              <Delete fontSize="small" />
              <Typography>{t("results_report_card_remove")}</Typography>
            </IconButton>
            <IconButton aria-label="move_up" onClick={handleUpButtonClick} size="small">
              <ArrowUpward fontSize="small" />
              <Typography>{t("results_report_card_move_up")}</Typography>
            </IconButton>
            <IconButton aria-label="move_down" onClick={handleDownButtonClick} size="small">
              <ArrowDownward fontSize="small" />
              <Typography>{t("results_report_card_move_down")}</Typography>
            </IconButton>
          </Box>
        </Box>
      </Box>
      {/* Alert message section */}
      <AlertMessage />
    </>
  );
};

ReportsCard.propTypes = {
  data: PropTypes.string.isRequired,
  id: PropTypes.string.isRequired,
  image: PropTypes.any.isRequired,
  isSelected: PropTypes.bool.isRequired,
  onCardClick: PropTypes.func.isRequired,
  onReportAction: PropTypes.func.isRequired,
  title: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
};

export default ReportsCard;
