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
    setAlertSeverity,
    setAlertShowMessage,
    setSelectedCountry,
    setSelectedHazard,
    setSelectedScenario,
    setSelectedExposureEconomic,
    setSelectedExposureNonEconomic,
    setSelectedTimeHorizon,
    setSelectedAnnualGrowth,
    setIsValidHazard,
    setIsValidExposureEconomic,
    setIsValidExposureNonEconomic,
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
              params: report.data,
              image: report.data.country_name === "thailand" ? outputIconTha : outputIconEgy,
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
    return reports.find((report) => report.id === id) || null;
  };

  const restoreScenario = async (id) => {
    try {
      const scenario = getScenario(id);

      if (!scenario) {
        throw new Error(`Scenario with id ${id} not found.`);
      }

      const scenarioData = scenario.data;
      const scenarioParams = scenario.params;

      setScenarioRunCode(id);
      setSelectedCountry(scenarioParams.country_name);
      setSelectedHazard(scenarioParams.hazard_type);
      setIsValidHazard(true);
      setSelectedScenario(scenarioParams.scenario);

      if (scenarioParams.exposure_economic) {
        setSelectedExposureEconomic(scenarioParams.exposure_economic);
        setIsValidExposureEconomic(true);
      } else {
        setSelectedExposureNonEconomic(scenarioParams.exposure_non_economic);
        setIsValidExposureNonEconomic(true);
      }

      setSelectedTimeHorizon([scenarioParams.ref_year, scenarioData.ref_year]);
      setSelectedAnnualGrowth(scenarioParams.annual_growth);
    } catch (error) {
      console.error("Error restoring scenario:", error);
      setAlertMessage("An error occurred while restoring the scenario.");
      setAlertSeverity("error");
    } finally {
      setAlertShowMessage(true);
    }
  };

  return {
    fetchReports,
    restoreScenario,
  };
};
