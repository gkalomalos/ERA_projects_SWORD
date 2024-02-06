import React from "react";

import AnnualGrowthCard from "./AnnualGrowthCard";
import CountryCard from "./CountryCard";
import ExposureEconomicCard from "./ExposureEconomicCard";
import ExposureNonEconomicCard from "./ExposureNonEconomicCard";
import HazardCard from "./HazardCard";
import ScenarioCard from "./ScenarioCard";
import TimeHorizonCard from "./TimeHorizonCard";

const ViewCard = (props) => {
  return (
    <>
      {props.selectedCard === "country" && (
        <CountryCard
          onCountrySelect={props.onChangeCountry}
          selectedCountry={props.selectedCountry}
        />
      )}
      {props.selectedCard === "hazard" && (
        <HazardCard
          onChangeValidHazard={props.onChangeValidHazard}
          onHazardSelect={props.onChangeHazard}
          selectedCountry={props.selectedCountry}
          selectedHazard={props.selectedHazard}
        />
      )}
      {props.selectedCard === "scenario" && (
        <ScenarioCard
          onScenarioSelect={props.onChangeScenario}
          selectedScenario={props.selectedScenario}
        />
      )}
      {props.selectedCard === "timeHorizon" && (
        <TimeHorizonCard
          onTimeHorizonSelect={props.onChangeTimeHorizon}
          selectedTimeHorizon={props.selectedTimeHorizon}
        />
      )}
      {props.selectedCard === "annualGrowth" && (
        <AnnualGrowthCard
          onGDPSelect={props.onChangeAnnualGDPGrowth}
          onPopulationSelect={props.onChangeAnnualPopulationGrowth}
          selectedAnnualGDPGrowth={props.selectedAnnualGDPGrowth}
          selectedAnnualPopulationGrowth={props.selectedAnnualPopulationGrowth}
        />
      )}
      {props.selectedCard === "exposureEconomic" && (
        <ExposureEconomicCard
          onChangeValidEconomicExposure={props.onChangeValidEconomicExposure}
          onExposureEconomicSelect={props.onChangeExposureEconomic}
          selectedCountry={props.selectedCountry}
          selectedExposureEconomic={props.selectedExposureEconomic}
        />
      )}
      {props.selectedCard === "exposureNonEconomic" && (
        <ExposureNonEconomicCard
          onChangeValidNonEconomicExposure={props.onChangeValidNonEconomicExposure}
          onExposureNonEconomicSelect={props.onChangeExposureNonEconomic}
          selectedCountry={props.selectedCountry}
          selectedExposureNonEconomic={props.selectedExposureNonEconomic}
        />
      )}
    </>
  );
};

export default ViewCard;
