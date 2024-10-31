import React from "react";

import CountryMacroCard from "./CountryMacroCard";
import HazardMacroCard from "./HazardMacroCard";
import MacroEconomicVariableCard from "./MacroEconomicVariableCard";
import ScenarioMacroCard from "./ScenarioMacroCard";
import SectorMacroCard from "./SectorMacroCard";
import useStore from "../../store";

const ViewMacroCard = () => {
  const { selectedMacroCard } = useStore();

  return (
    <>
      {selectedMacroCard === "country" && <CountryMacroCard />}
      {selectedMacroCard === "hazard" && <HazardMacroCard />}
      {selectedMacroCard === "scenario" && <ScenarioMacroCard />}
      {selectedMacroCard === "sector" && <SectorMacroCard />}
      {selectedMacroCard === "macroVariable" && <MacroEconomicVariableCard />}
    </>
  );
};

export default ViewMacroCard;
