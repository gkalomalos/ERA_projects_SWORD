import React from "react";
import { Box } from "@mui/material";
import MUITable from "./MUITable";

const MacroEconomicTable = () => {
  const data = [
    {
      table_macro_header_impact: "National GDP (annual average)",
      table_macro_header_without_cc: 100000000,
      table_macro_header_with_cc: 75000000,
      table_macro_header_with_adaptation: 40000000,
    },
    {
      table_macro_header_impact: "Agri GDP (annual average)",
      table_macro_header_without_cc: 200000000,
      table_macro_header_with_cc: 125000000,
      table_macro_header_with_adaptation: 60000000,
    },
  ];

  return (
    <Box
      sx={{
        margin: "auto",
        bgcolor: "#DCEFF2",
        border: "2px solid #3B919D",
        borderRadius: "16px",
        padding: "16px",
        marginBottom: "16px",
        overflow: "hidden", // Hide content that overflows outside the box
      }}
    >
      <Box
        sx={{
          height: "100%", // Ensure the child takes full height
          overflowY: "auto", // Enable vertical scrolling
        }}
      >
        <MUITable tableData={data} />
      </Box>
    </Box>
  );
};

export default MacroEconomicTable;
