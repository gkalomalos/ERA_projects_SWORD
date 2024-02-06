import React from "react";
import { useTranslation } from "react-i18next";

import { Box, Typography } from "@mui/material";

const MainViewTitle = ({ selectedTab, mapTitle }) => {
  const { t } = useTranslation();

  return (
    <Box sx={{ width: "100%" }}>
      <Typography
        variant="h6"
        component="div"
        sx={{
          margin: "auto",
          marginBottom: 2,
          bgcolor: "#F35A5A",
          color: "white",
          fontWeight: "bold",
          textAlign: "center",
          padding: "8px",
          borderRadius: "4px",
        }}
      >
        {t(`main_view_tab_${selectedTab}_title`)}
        {mapTitle ? `${mapTitle}` : ""}
      </Typography>
    </Box>
  );
};

export default MainViewTitle;
