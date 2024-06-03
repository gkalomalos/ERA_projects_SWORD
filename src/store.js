import { create } from "zustand";

const useStore = create((set, get) => ({
  activeMap: "hazard",
  isScenarioRunning: false,
  isValidExposureEconomic: false,
  isValidExposureNonEconomic: false,
  isValidHazard: false,
  mapTitle: "",
  modalMessage: "",
  selectedAnnualGrowth: 0,
  selectedAppOption: "",
  selectedCard: "country",
  selectedCountry: "",
  selectedExposureEconomic: "",
  selectedExposureFile: "",
  selectedExposureNonEconomic: "",
  selectedHazard: "",
  selectedHazardFile: "",
  selectedScenario: "",
  selectedTab: 0,
  selectedSubTab: 0,
  selectedTimeHorizon: [2024, 2050],

  setActiveMap: (map) => set({ activeMap: map }),
  setIsScenarioRunning: (data) => set({ isScenarioRunning: data }),
  setIsValidExposureEconomic: (isValid) => {
    const { selectedAppOption } = get();
    if (selectedAppOption === "era") {
      set({ isValidExposureEconomic: true });
    } else {
      set({ isValidExposureEconomic: isValid });
    }
  },
  setIsValidExposureNonEconomic: (isValid) => {
    const { selectedAppOption } = get();
    if (selectedAppOption === "era") {
      set({ isValidExposureNonEconomic: true });
    } else {
      set({ isValidExposureNonEconomic: isValid });
    }
  },
  setIsValidHazard: (isValid) => {
    const { selectedAppOption } = get();
    if (selectedAppOption === "era") {
      set({ isValidHazard: true });
    } else {
      set({ isValidHazard: isValid });
    }
  },
  setMapTitle: (data) => set({ mapTitle: data }),
  setModalMessage: (message) => set({ modalMessage: message }),
  setSelectedAnnualGrowth: (annualGrowth) => set({ selectedAnnualGrowth: annualGrowth }),
  setSelectedAppOption: (option) => set({ selectedAppOption: option }),
  setSelectedCard: (card) => set({ selectedCard: card }),
  setSelectedCountry: (country) => set({ selectedCountry: country }),
  setSelectedExposureEconomic: (exposureEconomic) =>
    set({ selectedExposureEconomic: exposureEconomic }),
  setSelectedExposureFile: (exposureFile) => set({ selectedExposureFile: exposureFile }),
  setSelectedExposureNonEconomic: (exposureNonEconomic) =>
    set({ selectedExposureNonEconomic: exposureNonEconomic }),
  setSelectedHazard: (hazard) => set({ selectedHazard: hazard }),
  setSelectedHazardFile: (hazardFile) => set({ selectedHazardFile: hazardFile }),
  setSelectedScenario: (scenario) => set({ selectedScenario: scenario }),
  setSelectedTab: (tab) => set({ selectedTab: tab, selectedSubTab: 0 }),
  setSelectedSubTab: (subTab) => set({ selectedSubTab: subTab }),
  setSelectedTimeHorizon: (timeHorizon) => set({ selectedTimeHorizon: timeHorizon }),
}));

export default useStore;
