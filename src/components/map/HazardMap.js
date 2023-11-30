import React, { useEffect, useState, useRef } from "react";

import Button from "@mui/material/Button";
import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import { scaleSequential } from "d3-scale";
import { interpolateRdYlGn } from "d3-scale-chromatic";
import "leaflet/dist/leaflet.css";

const adminLayers = [0, 1, 2]; // Administrative layers
const returnPeriods = [10, 50, 100, 250]; // Return periods

const HazardMap = ({ activeMap, selectedCountry }) => {
  const [mapInfo, setMapInfo] = useState({ geoJson: null, colorScale: null });
  const [activeRPLayer, setActiveRPLayer] = useState(null);
  const [activeAdminLayer, setActiveAdminLayer] = useState(null);
  const mapRef = useRef();

  const fetchGeoJson = async (layer, rp) => {
    try {
      const tempPath = await window.electron.fetchTempDir();
      const response = await fetch(`${tempPath}/${activeMap}_geodata.json`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      const filteredFeatures = data.features.filter(
        (feature) =>
          feature.properties.layer === layer && feature.properties.hasOwnProperty(`rp${rp}`)
      );
      const filteredData = { ...data, features: filteredFeatures };
      const values = filteredFeatures.map((f) => f.properties[`rp${rp}`]);
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
    await fetchGeoJson(newLayer, returnPeriods[0]);
    setActiveAdminLayer(newLayer);
    setActiveRPLayer(returnPeriods[0]);
  };

  const handleRPLayerChange = async (rp) => {
    await fetchGeoJson(activeAdminLayer, rp);
    setActiveRPLayer(rp);
  };

  const style = (feature) => {
    return {
      fillColor: mapInfo.colorScale
        ? mapInfo.colorScale(feature.properties[`rp${activeRPLayer}`])
        : "#FFF",
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

  const RPButtonStyle = (rp) => ({
    flexGrow: 0,
    margin: 1,
    minWidth: "60px",
    maxWidth: "60px",
    fontSize: "0.75rem",
    bgcolor: rp === activeRPLayer ? "#2A4D69" : "#5C87B1",
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
    Egypt: [26.8206, 30.8025],
    Thailand: [15.87, 100.9925],
  };

  const onEachFeature = (feature, layer) => {
    if (feature.properties) {
      const country = feature.properties["COUNTRY"];
      const value = feature.properties.value;
      if (activeAdminLayer == 0) {
        layer.bindPopup(`Country: ${country}<br>Value: ${value}`);
      }
      if (activeAdminLayer == 1) {
        const name1 = feature.properties["NAME_1"];
        layer.bindPopup(`Country: ${country}<br>Admin 1: ${name1}<br>Value: ${value}`);
      }
      if (activeAdminLayer == 2) {
        const name1 = feature.properties["NAME_1"];
        const name2 = feature.properties["NAME_2"];
        layer.bindPopup(
          `Country: ${country}<br>Admin 1: ${name1}<br>Admin 2: ${name2}<br>Value: ${value}`
        );
      }
    }
  };

  useEffect(() => {
    if (activeMap && activeAdminLayer !== null && activeRPLayer !== null) {
      fetchGeoJson(activeAdminLayer, activeRPLayer);
    }
  }, [activeRPLayer, activeAdminLayer, activeMap]);

  useEffect(() => {
    if (mapRef.current && selectedCountry in countryCoordinates) {
      mapRef.current.flyTo(countryCoordinates[selectedCountry], 6);
    }
  }, [selectedCountry]);

  return (
    <MapContainer
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
            Admin{layer}
          </Button>
        ))}
        {returnPeriods.map((rp) => (
          <Button
            key={`rp-${rp}`}
            size="small"
            sx={RPButtonStyle(rp)}
            onClick={() => handleRPLayerChange(rp)}
            variant="contained"
          >
            RP{rp}
          </Button>
        ))}
      </div>
      {mapInfo.geoJson && mapInfo.colorScale && (
        <GeoJSON
          key={`${selectedCountry}-${activeAdminLayer}-${activeRPLayer}`}
          data={mapInfo.geoJson}
          style={style}
          onEachFeature={onEachFeature}
        />
      )}
    </MapContainer>
  );
};

export default HazardMap;
