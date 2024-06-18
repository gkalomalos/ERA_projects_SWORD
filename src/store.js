import { create } from "zustand";

const useStore = create((set, get) => ({
  activeMap: "hazard",
  alertMessage: "",
  alertSeverity: "info",
  alertShowMessage: false,
  isScenarioRunning: false,
  isValidExposureEconomic: false,
  isValidExposureNonEconomic: false,
  isValidHazard: false,
  mapTitle: "",
  modalMessage: "",
  progress: 0,
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
  viewControl: "display_map",

  setActiveMap: (map) => set({ activeMap: map }),
  setAlertMessage: (message) => set({ alertMessage: message }),
  setAlertSeverity: (severity) => set({ alertSeverity: severity }),
  setAlertShowMessage: (show) => set({ alertShowMessage: show }),
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
  setProgress: (newProgress) => set({ progress: newProgress }),
  setSelectedAnnualGrowth: (annualGrowth) => set({ selectedAnnualGrowth: annualGrowth }),
  setSelectedAppOption: (option) => set({ selectedAppOption: option }),
  setSelectedCard: (card) => set({ selectedCard: card }),
  setSelectedCountry: (country) => {
    set({
      selectedCountry: country,
      selectedAnnualGrowth: 0,
      selectedExposureEconomic: "",
      selectedExposureFile: "",
      selectedExposureNonEconomic: "",
      selectedHazard: "",
      selectedHazardFile: "",
      selectedScenario: "",
      selectedTimeHorizon: [2024, 2050],
      isValidExposureEconomic: false,
      isValidExposureNonEconomic: false,
      isValidHazard: false,
    });
  },
  setSelectedExposureEconomic: (exposureEconomic) => {
    set({ selectedExposureEconomic: exposureEconomic, selectedAnnualGrowth: 0 });
  },
  setSelectedExposureNonEconomic: (exposureNonEconomic) => {
    set({ selectedExposureNonEconomic: exposureNonEconomic, selectedAnnualGrowth: 0 });
  },
  setSelectedHazard: (hazard) => {
    set({ selectedHazard: hazard, selectedScenario: "" });
  },
  setSelectedExposureFile: (exposureFile) => set({ selectedExposureFile: exposureFile }),
  setSelectedHazardFile: (hazardFile) => set({ selectedHazardFile: hazardFile }),
  setSelectedScenario: (scenario) => set({ selectedScenario: scenario }),
  setSelectedTab: (tab) => set({ selectedTab: tab, selectedSubTab: 0 }),
  setSelectedSubTab: (subTab) => set({ selectedSubTab: subTab }),
  setSelectedTimeHorizon: (timeHorizon) => set({ selectedTimeHorizon: timeHorizon }),
  setViewControl: (control) => set({ viewControl: control }),
}));

export default useStore;
