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
  const { macroEconomicChartData, macroEconomicChartTitle } = useStore();

  const hasData = macroEconomicChartData?.datasets?.length > 0;

  const transformedData = hasData
    ? {
        labels: macroEconomicChartData.years,
        datasets: [
          {
            label: "With adaptation",
            data: macroEconomicChartData.datasets[0].data,
            borderColor: "rgba(75, 192, 192, 1)",
            backgroundColor: "rgba(75, 192, 192, 0.2)",
            fill: true,
            tension: 0.4,
          },
          {
            label: "Without adaptation",
            data: macroEconomicChartData.datasets[1].data,
            borderColor: "rgba(255, 99, 132, 1)",
            backgroundColor: "rgba(255, 99, 132, 0.2)",
            fill: true,
            tension: 0.4,
          },
        ],
      }
    : {
        datasets: [],
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
          {hasData ? (
            <Line data={transformedData} options={options} />
          ) : (
            <Typography variant="h6" align="center" color="textSecondary">
              No data available
            </Typography>
          )}
        </div>
      </Box>
    </Box>
  );
};

export default MacroEconomicChart;
