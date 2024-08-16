import { useTranslation } from "react-i18next";

import L from "leaflet";
import "leaflet-simple-map-screenshoter";

import useStore from "../store";
import APIService from "../APIService";
import outputIconTha from "../assets/folder_grey_network_icon_512.png";
import outputIconEgy from "../assets/folder_grey_cloud_icon_512.png";

export const useMapTools = () => {
  const { t } = useTranslation();
  const {
    activeMap,
    activeMapRef,
    addReport,
    isScenarioRunCompleted,
    scenarioRunCode,
    setAlertMessage,
    setAlertSeverity,
    setAlertShowMessage,
    selectedAnnualGrowth,
    selectedCountry,
    selectedExposureEconomic,
    selectedExposureNonEconomic,
    selectedHazard,
    selectedScenario,
    selectedTimeHorizon,
  } = useStore();

  const takeScreenshot = (map, filePath) => {
    return new Promise((resolve, reject) => {
      const screenshoter = L.simpleMapScreenshoter().addTo(map);
      screenshoter
        .takeScreen("blob")
        .then((blob) => {
          const reader = new FileReader();
          reader.onloadend = () => {
            const base64data = reader.result.split(",")[1];
            window.electron.saveScreenshot(base64data, filePath);
          };
          reader.readAsDataURL(blob);
        })
        .catch((e) => {
          console.error(e);
          reject(e); // Reject the promise if an error occurs
        });

      // Listen for the save screenshot response
      window.electron.onSaveScreenshotReply((event, { success, error, filePath }) => {
        if (success) {
          setAlertMessage("Screenshot saved successfully!");
          setAlertSeverity("success");
          setAlertShowMessage(true);
          resolve(filePath); // Resolve the promise with the file path on success
        } else {
          setAlertMessage(`Failed to save screenshot: ${error}`);
          setAlertSeverity("error");
          setAlertShowMessage(true);
          reject(new Error(error)); // Reject the promise on error
        }
      });
    });
  };

  const handleAddToOutput = () => {
    if (isScenarioRunCompleted) {
      APIService.AddToOutput(scenarioRunCode)
        .then((response) => {
          setAlertMessage(response.result.status.message);
          if (response.result.status.code === 2000) {
            setAlertSeverity("success");

            const outputData = {
              id: `${scenarioRunCode}_${new Date().getTime().toString()}`,
              data: `${selectedCountry} - ${selectedHazard} - ${selectedScenario} - ${
                selectedExposureEconomic ? selectedExposureEconomic : selectedExposureNonEconomic
              } - ${selectedTimeHorizon} - ${selectedAnnualGrowth}`,
              image: selectedCountry === "thailand" ? outputIconTha : outputIconEgy,
              title: `Impact data of ${t(`results_report_card_hazard_${selectedHazard}`)} on ${
                selectedExposureEconomic
                  ? t(`results_report_card_exposure_${selectedExposureEconomic}`)
                  : t(`results_report_card_exposure_${selectedExposureNonEconomic}`)
              } in ${t(`results_report_card_country_${selectedCountry}`)}`,
              type: t("results_report_card_output_data"),
            };
            addReport(outputData);
          } else {
            setAlertSeverity("error");
          }
          setAlertShowMessage(true);
        })
        .catch((error) => {
          console.log(error);
        });
    }
  };

  const getSaveMapTitle = () => {
    let title = "";
    if (activeMap === "hazard") {
      title = `${t(`results_report_card_hazard_type_${activeMap}`)} map of ${t(
        `results_report_card_hazard_${selectedHazard}`
      )} in ${t(`results_report_card_country_${selectedCountry}`)}`;
    } else if (activeMap === "exposure") {
      title = `${t(`results_report_card_hazard_type_${activeMap}`)} map of ${
        selectedExposureEconomic
          ? t(`results_report_card_exposure_${selectedExposureEconomic}`)
          : t(`results_report_card_exposure_${selectedExposureNonEconomic}`)
      } in ${t(`results_report_card_country_${selectedCountry}`)}`;
    } else {
      title = `${t(`results_report_card_hazard_type_${activeMap}`)} map of ${t(
        `results_report_card_hazard_${selectedHazard}`
      )} on ${
        selectedExposureEconomic
          ? t(`results_report_card_exposure_${selectedExposureEconomic}`)
          : t(`results_report_card_exposure_${selectedExposureNonEconomic}`)
      } in ${t(`results_report_card_country_${selectedCountry}`)}`;
    }

    return title;
  };

  const handleSaveMap = async () => {
    const reportPath = await window.electron.fetchReportDir();

    if (isScenarioRunCompleted && activeMapRef) {
      const id = new Date().getTime().toString();
      const filepath = `${reportPath}\\${scenarioRunCode}\\${activeMap}_${id}.png`;
      takeScreenshot(activeMapRef, filepath)
        .then(() => {
          const outputData = {
            id: id,
            data: `${selectedCountry} - ${selectedHazard} - ${selectedScenario} - ${
              selectedExposureEconomic ? selectedExposureEconomic : selectedExposureNonEconomic
            } - ${selectedTimeHorizon} - ${selectedAnnualGrowth}`,
            image: filepath,
            title: getSaveMapTitle(),
            type: t("results_report_card_map_data"),
          };
          addReport(outputData);
        })
        .catch((error) => {
          console.error("Error in taking screenshot or saving it:", error);
        });
    }
  };

  return {
    takeScreenshot,
    handleAddToOutput,
    handleSaveMap,
  };
};
