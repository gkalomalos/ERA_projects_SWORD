import React, { useState } from "react";
import { useTranslation } from "react-i18next";

import {
  Box,
  Button,
  Card,
  CardActionArea,
  CardContent,
  IconButton,
  Typography,
} from "@mui/material";
import CloseIcon from "@mui/icons-material/Close";

import APIService from "../../APIService";
import useStore from "../../store";

const exposureNonEconomicDict = {
  thailand: {
    flood: [
      "tree_crops_farmers",
      "grass_crops_farmers",
      "diarrhea_patients",
      "buddhist_monks",
      "roads",
      "students",
    ],
    drought: ["tree_crops_farmers", "grass_crops_farmers", "water_users"],
    heatwaves: ["buddhist_monks", "students"],
  },
  egypt: {
    flood: ["students", "diarrhea_patients", "roads"],
    heatwaves: ["hospitalised_people", "students"],
  },
};

const ExposureNonEconomicCard = () => {
  const {
    selectedAppOption,
    selectedCountry,
    selectedExposureNonEconomic,
    selectedExposureFile,
    selectedHazard,
    setAlertMessage,
    setAlertSeverity,
    setAlertShowMessage,
    setIsValidExposureNonEconomic,
    setSelectedExposureFile,
    setSelectedExposureNonEconomic,
  } = useStore();
  const { t } = useTranslation();

  const [fetchExposureMessage, setFetchExposureMessage] = useState("");

  const exposuresNonEconomic = exposureNonEconomicDict[selectedCountry][selectedHazard] || [];

  const handleCardSelect = async (exposure) => {
    if (selectedExposureNonEconomic === exposure) {
      setSelectedExposureNonEconomic(""); // Deselect if already selected
    } else {
      setSelectedExposureNonEconomic(exposure);
    }
    // Clear the temp directory to reset maps
    await window.electron.clearTempDir();
    setSelectedExposureFile("");
    setIsValidExposureNonEconomic(false);
    setFetchExposureMessage("");
  };

  const isButtonSelected = (exposure) => selectedExposureNonEconomic === exposure;

  const handleLoadButtonClick = (event) => {
    // Reset the value of the fetched Exposure data if existing
    setFetchExposureMessage("");
    setSelectedExposureFile("");
    setIsValidExposureNonEconomic(false);
    const file = event.target.files[0];
    if (file) {
      setSelectedExposureFile(file.name);
      setIsValidExposureNonEconomic(true);
    }
  };

  const clearUploadedFile = () => {
    setSelectedExposureFile("");
    setIsValidExposureNonEconomic(false);
    // Reset the value of the file input to avoid issues when trying to upload the same file
    document.getElementById("exposure-non-economic-contained-button-file").value = "";
  };

  const clearFetchedData = () => {
    setFetchExposureMessage("");
    setIsValidExposureNonEconomic(false);
  };

  const handleFetchButtonClick = (event) => {
    // Reset the value of the file input if already selected
    setSelectedExposureFile("");
    setFetchExposureMessage("");
    setIsValidExposureNonEconomic(false);
    const body = {
      country: selectedCountry,
      dataType: selectedExposureNonEconomic,
    };
    APIService.CheckDataType(body)
      .then((response) => {
        setAlertMessage(response.result.status.message);
        response.result.status.code === 2000
          ? setAlertSeverity("success")
          : setAlertSeverity("error");
        setAlertShowMessage(true);
        setFetchExposureMessage(response.result.status.message);
        setIsValidExposureNonEconomic(response.result.status.code === 2000);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  return (
    <Card
      sx={{
        maxWidth: 800,
        margin: "auto",
        bgcolor: "#DCEFF2",
        border: "2px solid #3B919D",
        borderRadius: "16px",
      }}
    >
      <CardContent>
        <Typography
          gutterBottom
          variant="h5"
          component="div"
          color="text.primary"
          sx={{
            textAlign: "center",
            fontWeight: "bold",
            backgroundColor: "#F79191",
            borderRadius: "8px",
            padding: "8px",
            marginBottom: "24px",
          }}
        >
          {t("card_exposure_non_economic_title")}
        </Typography>

        {/* Non Economic Exposure selection section */}
        {exposuresNonEconomic.map((exposure) => (
          <CardActionArea
            key={exposure}
            onClick={() => handleCardSelect(exposure)}
            sx={{
              backgroundColor: isButtonSelected(exposure) ? "#F79191" : "#FFCCCC",
              borderRadius: "8px",
              margin: "16px", // Space around buttons
              marginLeft: 0,
              textAlign: "center",
              padding: "8px 0",
              transition: "transform 0.1s ease-in-out", // Add transition for transform
              "&:active": {
                transform: "scale(0.96)", // Slightly scale down when clicked
              },
            }}
          >
            <Typography variant="body1" color="text.primary" sx={{ textAlign: "center" }}>
              {t(`card_exposure_non_economic_${exposure}`)}
            </Typography>
          </CardActionArea>
        ))}

        {/* Load button section */}
        {selectedCountry && selectedAppOption === "explore" && (
          <Box sx={{ display: "flex", flexDirection: "row", justifyContent: "center" }}>
            <Box>
              <input
                accept=".xlsx"
                hidden
                id="exposure-non-economic-contained-button-file"
                multiple={false}
                onChange={handleLoadButtonClick}
                type="file"
              />
              <label htmlFor="exposure-non-economic-contained-button-file">
                <Button
                  component="span"
                  sx={{
                    bgcolor: "#FFEBEB",
                    color: "#000000",
                    fontWeight: "bold",
                    margin: 2,
                    "&:hover": { bgcolor: "#FFCCCC" },
                    transition: "transform 0.1s ease-in-out",
                    "&:active": {
                      transform: "scale(0.96)",
                    },
                  }}
                  variant="contained"
                >
                  {t("card_exposure_non_economic_load_button")}
                </Button>
              </label>
            </Box>

            {/* Fetch button section */}
            <Box>
              <Button
                component="span"
                sx={{
                  bgcolor: "#FFEBEB",
                  color: "#000000",
                  fontWeight: "bold",
                  margin: 2,
                  "&:hover": { bgcolor: "#FFCCCC" },
                  transition: "transform 0.1s ease-in-out", // Add transition for transform
                  "&:active": {
                    transform: "scale(0.96)", // Slightly scale down when clicked
                  },
                }}
                variant="contained"
                onClick={handleFetchButtonClick}
                disabled={true}
              >
                {t("card_exposure_non_economic_fetch_button")}
              </Button>
            </Box>
          </Box>
        )}

        {/* Display uploaded file name section */}
        {selectedExposureFile && selectedAppOption === "explore" && (
          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              marginTop: 2,
            }}
          >
            <Typography variant="body2" color="text.primary" sx={{ textAlign: "center" }}>
              {t("card_exposure_non_economic_upload_file")}: {selectedExposureFile}
            </Typography>
            <IconButton onClick={clearUploadedFile} size="small" sx={{ color: "#F35A5A" }}>
              <CloseIcon />
            </IconButton>
          </Box>
        )}

        {/* Display fetch Exposure data message section */}
        {fetchExposureMessage && (
          <Box
            sx={{
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
              marginTop: 2,
            }}
          >
            <Typography variant="body2" color="text.primary" sx={{ textAlign: "center" }}>
              {t("card_exposure_non_economic_fetch_exposure")}: {fetchExposureMessage}
            </Typography>
            <IconButton onClick={clearFetchedData} size="small" sx={{ color: "#F35A5A" }}>
              <CloseIcon />
            </IconButton>
          </Box>
        )}

        {/* Remarks section */}
        <Box sx={{ padding: 2, backgroundColor: "#F2F2F2", borderRadius: "8px" }}>
          <Typography variant="body2" color="text.primary">
            {t("card_exposure_non_economic_remarks")}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};

export default ExposureNonEconomicCard;
