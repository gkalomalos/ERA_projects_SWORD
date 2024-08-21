import { create } from "zustand";

import { generateRunCode } from "./utils/misc";

const useStore = create((set, get) => ({
  activeMap: "hazard",
  activeMapRef: null,
  activeViewControl: "display_map",
  alertMessage: "",
  alertSeverity: "info",
  alertShowMessage: false,
  isScenarioRunCompleted: false,
  isScenarioRunning: false,
  isValidExposureEconomic: false,
  isValidExposureNonEconomic: false,
  isValidHazard: false,
  mapTitle: "",
  modalMessage: "",
  progress: 0,
  reports: [],
  scenarioRunCode: "",
  selectedAnnualGrowth: 0,
  selectedAppOption: "",
  selectedCard: "country",
  selectedCountry: "",
  selectedExposureEconomic: "",
  selectedExposureFile: "",
  selectedExposureNonEconomic: "",
  selectedHazard: "",
  selectedHazardFile: "",
  selectedReportType: "",
  selectedScenario: "",
  selectedSubTab: 0,
  selectedTab: 0,
  selectedTimeHorizon: [2024, 2050],

  // Method to add a new report
  addReport: (newReport) =>
    set((state) => ({
      reports: [...state.reports, newReport],
    })),

  // Method to remove a report by id
  removeReport: (reportId) =>
    set((state) => ({
      reports: state.reports.filter((report) => report.id !== reportId),
    })),

  // Method to update reports
  updateReports: (newReports) =>
    set(() => ({
      reports: newReports,
    })),

  setActiveMap: (map) => set({ activeMap: map }),
  setActiveMapRef: (mapRef) => set({ activeMapRef: mapRef }),
  setAlertMessage: (message) => set({ alertMessage: message }),
  setAlertSeverity: (severity) => set({ alertSeverity: severity }),
  setAlertShowMessage: (show) => set({ alertShowMessage: show }),
  setIsScenarioRunCompleted: (data) => set({ isScenarioRunCompleted: data }),
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
  setScenarioRunCode: () => set({ scenarioRunCode: generateRunCode() }),
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
    set({
      selectedAnnualGrowth: 0,
      selectedExposureEconomic: "",
      selectedExposureFile: "",
      selectedExposureNonEconomic: "",
      selectedHazard: hazard,
      selectedScenario: "",
      selectedTimeHorizon: [2024, 2050],
      isValidExposureEconomic: false,
      isValidExposureNonEconomic: false,
    });
  },
  setSelectedExposureFile: (exposureFile) => set({ selectedExposureFile: exposureFile }),
  setSelectedHazardFile: (hazardFile) => set({ selectedHazardFile: hazardFile }),
  setSelectedReportType: (reportType) => set({ selectedReportType: reportType }),
  setSelectedScenario: (scenario) => set({ selectedScenario: scenario }),
  setSelectedSubTab: (subTab) => set({ selectedSubTab: subTab }),
  setSelectedTab: (tab) => set({ selectedTab: tab, selectedSubTab: 0 }),
  setSelectedTimeHorizon: (timeHorizon) => set({ selectedTimeHorizon: timeHorizon }),
  setActiveViewControl: (control) => set({ activeViewControl: control }),
}));

export default useStore;
