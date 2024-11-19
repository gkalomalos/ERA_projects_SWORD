import React from "react";
import { Box, Typography } from "@mui/material";
import { Line } from "react-chartjs-2";
import {
  CategoryScale,
  Chart as ChartJS,
  Filler,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
} from "chart.js";

import useStore from "../../store";

// Register all necessary elements
ChartJS.register(
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend,
  Filler
);

const MacroEconomicChart = () => {
  const {
    credOutputData,
    selectedMacroCountry,
    selectedMacroScenario,
    selectedMacroSector,
    selectedMacroVariable,
    macroEconomicChartTitle,
  } = useStore();

  // Filter data based on selected filters
  const filteredData = credOutputData.filter(
    (row) =>
      row.country === selectedMacroCountry &&
      row.scenario === selectedMacroScenario &&
      row.economic_sector === selectedMacroSector &&
      row.economic_indicator === selectedMacroVariable
  );

  // Group data by adaptation value
  const groupedData = filteredData.reduce((acc, row) => {
    const adaptationLabel =
      row.adpatation === null || row.adpatation === "None"
        ? "Without adaptation"
        : `${row.adpatation * 100}% Adaptation`;

    if (!acc[adaptationLabel]) {
      acc[adaptationLabel] = { years: [], values: [] };
    }
    acc[adaptationLabel].years.push(row.year);
    acc[adaptationLabel].values.push(row.proportion_change_from_baseline);

    return acc;
  }, {});

  // Transform data for Chart.js
  const datasets = Object.keys(groupedData).map((label) => ({
    label,
    data: groupedData[label].values,
    borderColor: label.includes("Without") ? "rgba(255, 99, 132, 1)" : "rgba(75, 192, 192, 1)", // Different colors for adaptation types
    backgroundColor: label.includes("Without")
      ? "rgba(255, 99, 132, 0.2)"
      : "rgba(75, 192, 192, 0.2)",
    fill: true,
    tension: 0.4,
  }));

  const transformedData = {
    labels: filteredData.length > 0 ? [...new Set(filteredData.map((row) => row.year))] : [],
    datasets,
  };

  const options = {
    scales: {
      x: { type: "category" },
      y: { beginAtZero: true },
    },
    plugins: {
      legend: { display: true },
      title: { display: true, text: macroEconomicChartTitle },
    },
  };

  return (
    <Box
      sx={{
        margin: "auto",
        bgcolor: "#DCEFF2",
        border: "2px solid #3B919D",
        borderRadius: "16px",
        padding: "16px",
        marginBottom: "16px",
        overflow: "hidden",
      }}
    >
      <Box sx={{ height: "100%", overflowY: "auto" }}>
        <div>
          {filteredData.length > 0 ? (
            <Line data={transformedData} options={options} />
          ) : (
            <Typography variant="h6" align="center" color="textSecondary">
              No data available for the selected filters
            </Typography>
          )}
        </div>
      </Box>
    </Box>
  );
};

export default MacroEconomicChart;
