import React from "react";
import PropTypes from "prop-types";

import AnnualGrowthCard from "./AnnualGrowthCard";
import CountryCard from "./CountryCard";
import ExposureEconomicCard from "./ExposureEconomicCard";
import ExposureNonEconomicCard from "./ExposureNonEconomicCard";
import HazardCard from "./HazardCard";
import ScenarioCard from "./ScenarioCard";
import TimeHorizonCard from "./TimeHorizonCard";

const ViewCard = ({
  onChangeAnnualGrowth,
  onChangeCountry,
  onChangeExposureEconomic,
  onChangeExposureFile,
  onChangeExposureNonEconomic,
  onChangeHazard,
  onChangeHazardFile,
  onChangeScenario,
  onChangeTimeHorizon,
  onChangeValidEconomicExposure,
  onChangeValidNonEconomicExposure,
  onChangeValidHazard,
  selectedAnnualGrowth,
  selectedAppOption,
  selectedCard,
  selectedCountry,
  selectedExposureEconomic,
  selectedExposureFile,
  selectedExposureNonEconomic,
  selectedHazard,
  selectedHazardFile,
  selectedScenario,
  selectedTimeHorizon,
}) => {
  return (
    <>
      {selectedCard === "country" && (
        <CountryCard onCountrySelect={onChangeCountry} selectedCountry={selectedCountry} />
      )}
      {selectedCard === "hazard" && (
        <HazardCard
          onChangeValidHazard={onChangeValidHazard}
          onChangeHazardFile={onChangeHazardFile}
          onHazardSelect={onChangeHazard}
          selectedAppOption={selectedAppOption}
          selectedCountry={selectedCountry}
          selectedHazard={selectedHazard}
          selectedHazardFile={selectedHazardFile}
        />
      )}
      {selectedCard === "scenario" && (
        <ScenarioCard
          onScenarioSelect={onChangeScenario}
          selectedHazard={selectedHazard}
          selectedScenario={selectedScenario}
        />
      )}
      {selectedCard === "timeHorizon" && (
        <TimeHorizonCard
          onTimeHorizonSelect={onChangeTimeHorizon}
          selectedTimeHorizon={selectedTimeHorizon}
        />
      )}
      {selectedCard === "annualGrowth" && (
        <AnnualGrowthCard
          onGrowthSelect={onChangeAnnualGrowth}
          selectedAnnualGrowth={selectedAnnualGrowth}
          selectedExposureEconomic={selectedExposureEconomic}
          selectedExposureNonEconomic={selectedExposureNonEconomic}
        />
      )}
      {selectedCard === "exposureEconomic" && (
        <ExposureEconomicCard
          onChangeExposureFile={onChangeExposureFile}
          onChangeValidEconomicExposure={onChangeValidEconomicExposure}
          onExposureEconomicSelect={onChangeExposureEconomic}
          selectedAppOption={selectedAppOption}
          selectedCountry={selectedCountry}
          selectedExposureFile={selectedExposureFile}
          selectedExposureEconomic={selectedExposureEconomic}
        />
      )}
      {selectedCard === "exposureNonEconomic" && (
        <ExposureNonEconomicCard
          onChangeExposureFile={onChangeExposureFile}
          onChangeValidNonEconomicExposure={onChangeValidNonEconomicExposure}
          onExposureNonEconomicSelect={onChangeExposureNonEconomic}
          selectedAppOption={selectedAppOption}
          selectedCountry={selectedCountry}
          selectedExposureFile={selectedExposureFile}
          selectedExposureNonEconomic={selectedExposureNonEconomic}
        />
      )}
    </>
  );
};

ViewCard.propTypes = {
  onChangeAnnualGrowth: PropTypes.func.isRequired,
  onChangeCountry: PropTypes.func.isRequired,
  onChangeExposureEconomic: PropTypes.func.isRequired,
  onChangeExposureFile: PropTypes.func.isRequired,
  onChangeExposureNonEconomic: PropTypes.func.isRequired,
  onChangeHazard: PropTypes.func.isRequired,
  onChangeHazardFile: PropTypes.func.isRequired,
  onChangeScenario: PropTypes.func.isRequired,
  onChangeTimeHorizon: PropTypes.func.isRequired,
  onChangeValidEconomicExposure: PropTypes.func.isRequired,
  onChangeValidNonEconomicExposure: PropTypes.func.isRequired,
  onChangeValidHazard: PropTypes.func.isRequired,

  selectedAnnualGrowth: PropTypes.number.isRequired,
  selectedAppOption: PropTypes.string.isRequired,
  selectedCard: PropTypes.string.isRequired,
  selectedCountry: PropTypes.string.isRequired,
  selectedExposureEconomic: PropTypes.string.isRequired,
  selectedExposureFile: PropTypes.string.isRequired,
  selectedExposureNonEconomic: PropTypes.string.isRequired,
  selectedHazard: PropTypes.string.isRequired,
  selectedHazardFile: PropTypes.string.isRequired,
  selectedScenario: PropTypes.string.isRequired,
  selectedTimeHorizon: PropTypes.array.isRequired,
};

export default ViewCard;
