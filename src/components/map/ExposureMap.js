import React, { useEffect, useState, useRef } from "react";
import { useTranslation } from "react-i18next";

import Button from "@mui/material/Button";
import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import { scaleSequential } from "d3-scale";
import { interpolateRdYlGn } from "d3-scale-chromatic";
import "leaflet/dist/leaflet.css";

const adminLayers = [0, 1, 2]; // Administrative layers

const ExposureMap = ({ selectedCountry }) => {
  const { t } = useTranslation();
  const [mapInfo, setMapInfo] = useState({ geoJson: null, colorScale: null });
  const [activeAdminLayer, setActiveAdminLayer] = useState(0);
  const mapRef = useRef();

  const fetchGeoJson = async (layer) => {
    try {
      const tempPath = await window.electron.fetchTempDir();
      const response = await fetch(`${tempPath}/exposures_geodata.json`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      const filteredFeatures = data.features.filter(
        (feature) => feature.properties.layer === layer
      );
      const filteredData = { ...data, features: filteredFeatures };
      const values = filteredFeatures.map((f) => f.properties.value);
      const minValue = Math.min(...values);
      const maxValue = Math.max(...values);
      const scale = scaleSequential(interpolateRdYlGn).domain([maxValue, minValue]);

      setMapInfo({ geoJson: filteredData, colorScale: scale });
    } catch (error) {
      console.error("Error fetching GeoJSON data:", error);
      setMapInfo({ geoJson: null, colorScale: null });
    }
  };

  const handleAdminLayerChange = async (newLayer) => {
    await fetchGeoJson(newLayer);
    setActiveAdminLayer(newLayer);
  };

  const style = (feature) => {
    return {
      fillColor: mapInfo.colorScale ? mapInfo.colorScale(feature.properties.value) : "#FFF",
      weight: 2,
      opacity: 1,
      color: "white",
      dashArray: "3",
      fillOpacity: 0.7,
    };
  };

  const adminButtonStyle = (layer) => ({
    flexGrow: 0,
    margin: 1,
    minWidth: "60px",
    maxWidth: "60px",
    fontSize: "0.75rem",
    bgcolor: layer === activeAdminLayer ? "#2A4D69" : "#5C87B1",
    "&:hover": { bgcolor: "#9886D6" },
  });

  const buttonContainerStyle = {
    position: "absolute",
    top: "10px",
    right: "10px",
    zIndex: 1000,
    display: "flex",
    flexDirection: "row",
  };

  const countryCoordinates = {
    egypt: [26.8206, 30.8025],
    thailand: [15.87, 100.9925],
  };

  const onEachFeature = (feature, layer) => {
    if (feature.properties) {
      const country = feature.properties["COUNTRY"];
      const value = feature.properties.value;
      if (activeAdminLayer === 0) {
        layer.bindPopup(
          `${t("map_exposure_popup_country")}: ${country}<br>${t(
            "map_exposure_popup_value"
          )}: ${value}`
        );
      }
      if (activeAdminLayer === 1) {
        const name1 = feature.properties["NAME_1"];
        layer.bindPopup(
          `${t("map_exposure_popup_country")}: ${country}<br>${t(
            "map_exposure_popup_admin1"
          )}: ${name1}<br>${t("map_exposure_popup_value")}: ${value}`
        );
      }
      if (activeAdminLayer === 2) {
        const name1 = feature.properties["NAME_1"];
        const name2 = feature.properties["NAME_2"];
        layer.bindPopup(
          `${t("map_exposure_popup_country")}: ${country}<br>${t(
            "map_exposure_popup_admin1"
          )}: ${name1}<br>${t("map_exposure_popup_admin2")}: ${name2}<br>${t(
            "map_exposure_popup_value"
          )}: ${value}`
        );
        layer.bindPopup(
          `${t("map_exposure_popup_country")}: ${country}<br>${t(
            "map_exposure_popup_admin1"
          )}: ${name1}<br>${t("map_exposure_popup_admin2")}: ${name2}<br>${t(
            "map_exposure_popup_value"
          )}: ${value}`
        );
      }
    }
  };

  useEffect(() => {
    if (activeAdminLayer !== null) {
      fetchGeoJson(activeAdminLayer);
    }
  }, [activeAdminLayer]);

  useEffect(() => {
    if (mapRef.current && selectedCountry in countryCoordinates) {
      mapRef.current.flyTo(countryCoordinates[selectedCountry], 6); // Change map center and zoom
    }
  }, [selectedCountry]);

  return (
    <MapContainer
      key={selectedCountry}
      center={countryCoordinates[selectedCountry] || [30.0, 31.0]}
      zoom={6}
      style={{ height: "100%", width: "100%" }}
      whenCreated={(mapInstance) => (mapRef.current = mapInstance)}
    >
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <div style={buttonContainerStyle}>
        {adminLayers.map((layer) => (
          <Button
            key={`admin-${layer}`}
            size="small"
            sx={adminButtonStyle(layer)}
            onClick={() => handleAdminLayerChange(layer)}
            variant="contained"
          >
            {t("map_exposure_button_admin")}
            {layer}
          </Button>
        ))}
      </div>
      {mapInfo.geoJson && mapInfo.colorScale && (
        <GeoJSON
          key={`${selectedCountry}-${activeAdminLayer}`}
          data={mapInfo.geoJson}
          style={style}
          onEachFeature={onEachFeature}
        />
      )}
    </MapContainer>
  );
};

export default ExposureMap;
