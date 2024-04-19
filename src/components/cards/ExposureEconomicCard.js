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
import AlertMessage from "../alerts/AlertMessage";

const exposureEconomicDict = {
  thailand: ["tree_crops", "grass_crops", "wet_markets"],
  egypt: ["crops", "livestock", "power_plants", "hotels"],
};

const ExposureEconomicCard = ({
  onChangeExposureFile,
  onChangeValidEconomicExposure,
  onExposureEconomicSelect,
  selectedAppOption,
  selectedCountry,
  selectedExposureEconomic,
  selectedExposureFile,
}) => {
  const { t } = useTranslation();

  const [fetchExposureMessage, setFetchExposureMessage] = useState("");
  const [message, setMessage] = useState("");
  const [severity, setSeverity] = useState("info");
  const [showMessage, setShowMessage] = useState(true);

  const exposuresEconomic = exposureEconomicDict[selectedCountry] || [];

  const handleCardSelect = (exposure) => {
    if (selectedExposureEconomic === exposure) {
      onExposureEconomicSelect(""); // Deselect if already selected
    } else {
      onExposureEconomicSelect(exposure);
    }
    onChangeExposureFile("");
    onChangeValidEconomicExposure(false);
    setFetchExposureMessage("");
  };

  const isButtonSelected = (exposure) => selectedExposureEconomic === exposure;

  const handleLoadButtonClick = (event) => {
    // Reset the value of the fetched Exposure data if existing
    setFetchExposureMessage("");
    onChangeExposureFile("");
    onChangeValidEconomicExposure(false);
    const file = event.target.files[0];
    if (file) {
      onChangeExposureFile(file.name);
      onChangeValidEconomicExposure(true);
    }
  };

  const handleCloseMessage = () => {
    setShowMessage(false);
  };

  const clearUploadedFile = () => {
    onChangeExposureFile("");
    onChangeValidEconomicExposure(false);
    // Reset the value of the file input to avoid issues when trying to upload the same file
    document.getElementById("exposure-economic-contained-button-file").value = "";
  };

  const clearFetchedData = () => {
    setFetchExposureMessage("");
    onChangeValidEconomicExposure(false);
  };

  const handleFetchButtonClick = (event) => {
    // Reset the value of the file input if already selected
    onChangeExposureFile("");
    setFetchExposureMessage("");
    onChangeValidEconomicExposure(false);
    const body = {
      country: selectedCountry,
      dataType: selectedExposureEconomic,
    };
    APIService.CheckDataType(body)
      .then((response) => {
        setMessage(response.result.status.message);
        response.result.status.code === 2000 ? setSeverity("success") : setSeverity("error");
        setShowMessage(true);
        setFetchExposureMessage(response.result.status.message);
        onChangeValidEconomicExposure(response.result.status.code === 2000);
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
          {t("card_exposure_economic_title")}
        </Typography>

        {/* Economic Exposure selection section */}
        {exposuresEconomic.map((exposure) => (
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
              {t(`card_exposure_economic_${exposure}`)}
            </Typography>
          </CardActionArea>
        ))}

        {/* Load button section */}
        {selectedCountry && selectedAppOption === "explore" && (
          <Box sx={{ display: "flex", flexDirection: "row", justifyContent: "center" }}>
            <Box>
              <input
                accept=".xlsx,.hdf5"
                hidden
                id="exposure-economic-contained-button-file"
                multiple={false}
                onChange={handleLoadButtonClick}
                type="file"
              />
              <label htmlFor="exposure-economic-contained-button-file">
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
                  {t("card_exposure_economic_load_button")}
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
              >
                {t("card_exposure_economic_fetch_button")}
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
              {t("card_exposure_economic_upload_file")}: {selectedExposureFile}
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
              {t("card_exposure_economic_fetch_exposure")}: {fetchExposureMessage}
            </Typography>
            <IconButton onClick={clearFetchedData} size="small" sx={{ color: "#F35A5A" }}>
              <CloseIcon />
            </IconButton>
          </Box>
        )}

        {/* Remarks section */}
        <Box sx={{ padding: 2, backgroundColor: "#F2F2F2", borderRadius: "8px" }}>
          <Typography variant="body2" color="text.primary">
            {t("card_exposure_economic_remarks")}
          </Typography>
        </Box>
      </CardContent>

      {/* Alert message section */}
      {message && showMessage && (
        <AlertMessage
          handleCloseMessage={handleCloseMessage}
          message={message}
          severity={severity}
          showMessage={showMessage}
        />
      )}
    </Card>
  );
};

export default ExposureEconomicCard;
