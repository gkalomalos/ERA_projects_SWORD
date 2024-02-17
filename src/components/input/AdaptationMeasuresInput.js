import React, { useEffect, useState } from "react";

import { useTranslation } from "react-i18next";
import { Box, Card, CardContent, Typography } from "@mui/material";

import AdaptationMeasuresViewTitle from "../title/AdaptationMeasuresViewTitle";
import APIService from "../../APIService";

const AdaptationMeasuresInput = ({ selectedHazard }) => {
  const { t } = useTranslation();
  const [adaptationMeasures, setAdaptationMeasures] = useState([]);

  const onFetchAdaptationMeasuresHandler = () => {
    const body = {
      hazardType: selectedHazard,
    };
    APIService.FetchAdaptationMeasures(body)
      .then((response) => {
        console.log("response", response);
        console.log("response.result.data.adaptationMeasures", response.result.data.adaptationMeasures);
        setAdaptationMeasures(response.result.data.adaptationMeasures);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  useEffect(() => {
    if (selectedHazard) {
      console.log('fetching adaptation measures')
      onFetchAdaptationMeasuresHandler();
    }
  }, [selectedHazard]);

  return (
    <>
      <AdaptationMeasuresViewTitle />
      {adaptationMeasures ? (
        <Box sx={{ mt: 2 }}>
          {adaptationMeasures.map((measureName, index) => (
            <Card
              key={index}
              variant="outlined"
              sx={{
                bgcolor: "#EBF3F5",
                mb: 2,
              }}
            >
              <CardContent sx={{ p: 2 }}>
                <Typography gutterBottom variant="h6" component="div">
                  {measureName}
                </Typography>
              </CardContent>
            </Card>
          ))}
        </Box>
      ) : (
        <Typography sx={{ mt: 2, textAlign: "center" }}>
          {t("adaptation_input_no_measures")} {/* Display a message if no measures are found */}
        </Typography>
      )}
    </>
  );
};

export default AdaptationMeasuresInput;
