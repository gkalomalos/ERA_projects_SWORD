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
          onChangeHazardFile={props.onChangeHazardFile}
          onHazardSelect={props.onChangeHazard}
          selectedAppOption={props.selectedAppOption}
          selectedCountry={props.selectedCountry}
          selectedHazard={props.selectedHazard}
          selectedHazardFile={props.selectedHazardFile}
        />
      )}
      {props.selectedCard === "scenario" && (
        <ScenarioCard
          onScenarioSelect={props.onChangeScenario}
          selectedHazard={props.selectedHazard}
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
          onGrowthSelect={props.onChangeAnnualGrowth}
          selectedAnnualGrowth={props.selectedAnnualGrowth}
          selectedExposureEconomic={props.selectedExposureEconomic}
          selectedExposureNonEconomic={props.selectedExposureNonEconomic}
        />
      )}
      {props.selectedCard === "exposureEconomic" && (
        <ExposureEconomicCard
          onChangeExposureFile={props.onChangeExposureFile}
          onChangeValidEconomicExposure={props.onChangeValidEconomicExposure}
          onExposureEconomicSelect={props.onChangeExposureEconomic}
          selectedAppOption={props.selectedAppOption}
          selectedCountry={props.selectedCountry}
          selectedExposureFile={props.selectedExposureFile}
          selectedExposureEconomic={props.selectedExposureEconomic}
        />
      )}
      {props.selectedCard === "exposureNonEconomic" && (
        <ExposureNonEconomicCard
          onChangeExposureFile={props.onChangeExposureFile}
          onChangeValidNonEconomicExposure={props.onChangeValidNonEconomicExposure}
          onExposureNonEconomicSelect={props.onChangeExposureNonEconomic}
          selectedAppOption={props.selectedAppOption}
          selectedCountry={props.selectedCountry}
          selectedExposureFile={props.selectedExposureFile}
          selectedExposureNonEconomic={props.selectedExposureNonEconomic}
        />
      )}
    </>
  );
};

export default ViewCard;
