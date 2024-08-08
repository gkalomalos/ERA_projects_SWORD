import React from "react";
import { useTranslation } from "react-i18next";

import { Box, Button, Tabs, Tab, Paper } from "@mui/material";

import useStore from "../../store";
import AlertMessage from "../alerts/AlertMessage";
import APIService from "../../APIService";
import { takeScreenshot } from "../../utils/mapTools";
import outputIconTha from "../../assets/folder_grey_network_icon_512.png";
import outputIconEgy from "../../assets/folder_grey_cloud_icon_512.png";

const MainSubTabs = () => {
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
    selectedSubTab,
    selectedTab,
    setSelectedSubTab,
  } = useStore();

  const subTabsMap = {
    0: [], // Subtabs for "Parameters section"
    1: ["Risk", "Adaptation", "+ Add to Output", "+ Save Map"], // Added "Save to Map" button
    2: ["Risk", "Adaptation"], // Subtabs for "Macroeconomic (in dev) section"
    3: [], // Subtabs for "Outputs (reporting) section"
  };

  const handleAddToOutput = () => {
    if (isScenarioRunCompleted) {
      APIService.AddToOutput(scenarioRunCode)
        .then((response) => {
          // Handle the response and set alert messages
          setAlertMessage(response.result.status.message);
          if (response.result.status.code === 2000) {
            setAlertSeverity("success");

            // Create output data and add report
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

  const handleSubTabChange = (event, newValue) => {
    setSelectedSubTab(newValue);
  };

  const subTabs = subTabsMap[selectedTab];
  if (!subTabs) {
    return null; // This main tab does not have subtabs
  }

  return (
    <Paper
      square
      sx={{
        position: "fixed",
        top: "128px",
        zIndex: (theme) => theme.zIndex.drawer + 1,
        width: "100%",
        bgcolor: "#8AC8D0",
      }}
    >
      <Tabs
        value={selectedSubTab}
        onChange={handleSubTabChange}
        aria-label={`sub navigation tabs for main tab ${selectedTab}`}
        textColor="inherit"
        indicatorColor="secondary"
        variant="fullWidth"
        centered
        sx={{
          minHeight: 24,
          ".Mui-selected": { bgcolor: "#45ABB9", color: "#fff" },
          ".MuiTab-root": {
            color: "#fff",
            fontSize: "0.875rem", // Smaller text
            minHeight: 24, // Reduce the height of the tabs
            padding: "6px 12px", // Reduce the padding around the text
          },
          ".MuiTabs-indicator": {
            height: 2, // Smaller indicator height
          },
          ".MuiTab-root:not(.Mui-selected)": { bgcolor: "#8AC8D0" },
        }}
      >
        {subTabs.map((label, index) =>
          // Conditionally render a button instead of a tab for "+ Add to Output" and "Save to Map"
          index === 2 || index === 3 ? (
            <Box
              key={index}
              sx={{ position: "absolute", top: 0, right: index === 2 ? 100 : index === 3 ? 0 : 8 }}
            >
              <Button
                variant="contained"
                size="small"
                sx={{
                  bgcolor: "#FFCCCC",
                  transition: "transform 0.1s ease-in-out",
                  "&:active": {
                    transform: "scale(0.96)",
                  },
                  "&:hover": { bgcolor: "#F79191" },
                  textTransform: "none",
                }}
                onClick={index === 2 ? handleAddToOutput : handleSaveMap}
              >
                {label}
              </Button>
            </Box>
          ) : (
            <Tab key={index} label={label} sx={{ minHeight: 24 }} /> // Apply the reduced height
          )
        )}
      </Tabs>
      <AlertMessage />
    </Paper>
  );
};

export default MainSubTabs;
