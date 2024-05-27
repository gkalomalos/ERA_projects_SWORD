import React from "react";
import PropTypes from "prop-types";

import { Box } from "@mui/material";

import ResultsViewTitle from "../title/ResultsViewTitle";
import EconomicResultsCard from "./EconomicResultsCard";
import MacroEconomicResultsCard from "./MacroEconomicResultsCard";
import OutputResultsCard from "./OutputResultsCard";

const ResultsView = ({ selectedTab, onChangeActiveMap }) => {
  return (
    <Box sx={{ width: "100%" }}>
      <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
        <ResultsViewTitle selectedTab={selectedTab} />
        {selectedTab === 1 && <EconomicResultsCard onActiveMapSelect={onChangeActiveMap} />}
        {selectedTab === 2 && <MacroEconomicResultsCard />}
        {selectedTab === 3 && <OutputResultsCard />}
      </Box>
    </Box>
  );
};

ResultsView.propTypes = {
  selectedTab: PropTypes.number.isRequired,
  onChangeActiveMap: PropTypes.func.isRequired,
};

export default ResultsView;
