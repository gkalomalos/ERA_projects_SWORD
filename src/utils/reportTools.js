import { useTranslation } from "react-i18next";

import APIService from "../APIService";
import useStore from "../store";

import outputIconTha from "../assets/folder_grey_network_icon_512.png";
import outputIconEgy from "../assets/folder_grey_cloud_icon_512.png";

export const useReportTools = () => {
  const { t } = useTranslation();
  const {
    reports,
    addReport,
    setAlertMessage,

    selectedCountry,
    selectedExposureEconomic,
    selectedExposureNonEconomic,
    selectedHazard,
    selectedScenario,
    selectedAnnualGrowth,
    selectedTimeHorizon,

    setAlertSeverity,
    setAlertShowMessage,
    setSelectedCountry,
    setSelectedHazard,
    setSelectedScenario,
    setSelectedExposureEconomic,
    setSelectedExposureNonEconomic,
    setSelectedTimeHorizon,
    setSelectedAnnualGrowth,
    setScenarioRunCode,
  } = useStore.getState();

  const fetchReports = async () => {
    try {
      const response = await APIService.FetchReports();
      const { data, status } = response.result;

      if (status.code === 2000) {
        // Loop through each report and add it to the store if it doesn't already exist
        data.forEach((report) => {
          const existingReport = reports.find((r) => r.id === report.id);

          if (!existingReport) {
            const reportData = {
              id: report.id,
              data: `${report.data.country_name} - ${report.data.hazard_type} - ${
                report.data.scenario
              } - ${
                report.data.exposure_economic
                  ? report.data.exposure_economic
                  : report.data.exposure_non_economic
              } - ${report.data.ref_year},${report.data.ref_year} - ${report.data.annual_growth} `,
              image: report.data.country_name === "Thailand" ? outputIconTha : outputIconEgy,
              title: `Impact data of ${t(
                `results_report_card_hazard_${report.data.hazard_type}`
              )} on ${
                report.data.exposure_economic
                  ? t(`results_report_card_exposure_${report.data.exposure_economic}`)
                  : t(`results_report_card_exposure_${report.data.exposure_non_economic}`)
              } in ${t(`results_report_card_country_${report.data.country_name.toLowerCase()}`)}`,
              type: report.type,
            };
            addReport(reportData);
          }
        });
      } else {
        setAlertMessage(`Failed to fetch reports: ${status.message}`);
        setAlertSeverity("error");
      }
    } catch (error) {
      console.error("Error fetching reports:", error);
      setAlertMessage("An error occurred while fetching reports.");
      setAlertSeverity("error");
    } finally {
      setAlertShowMessage(true);
    }
  };

  const getScenario = (id) => {
    try {
      const scenario = reports.find((scenario) => scenario.id === id);
      if (!scenario) {
        throw new Error(`Scenario with id ${id} not found.`);
      }
      return scenario;
    } catch (error) {
      console.error(error.message);
      return null;
    }
  };

  const restoreScenario = async (id) => {
    try {
      const scenario = getScenario(id);

      if (!scenario) {
        throw new Error("Scenario could not be restored because it was not found.");
      }

      const scenarioData = scenario.data;

      // Update parameters in the correct order
      await setSelectedCountry(scenarioData.country_name);
      await setSelectedHazard(scenarioData.hazard_type);
      await setSelectedScenario(scenarioData.scenario);

      if (scenarioData.exposure_economic) {
        await setSelectedExposureEconomic(scenarioData.exposure_economic);
      } else {
        await setSelectedExposureNonEconomic(scenarioData.exposure_non_economic);
      }

      await setSelectedTimeHorizon([scenarioData.ref_year, scenarioData.future_year]);
      await setSelectedAnnualGrowth(scenarioData.annual_growth);
      await setScenarioRunCode(id);
    } catch (error) {
      console.error("Error in restoreScenario:", error.message);
      console.log("selectedCountry:", selectedCountry);
      console.log("selectedExposureEconomic:", selectedExposureEconomic);
      console.log("selectedExposureNonEconomic:", selectedExposureNonEconomic);
      console.log("selectedHazard:", selectedHazard);
      console.log("selectedScenario:", selectedScenario);
      console.log("selectedAnnualGrowth:", selectedAnnualGrowth);
      console.log("selectedTimeHorizon:", selectedTimeHorizon);
      return null;
    }
  };

  return {
    fetchReports,
    restoreScenario,
  };
};
