import React, { useEffect, useState, useRef } from "react";
import PropTypes from "prop-types";
import { useTranslation } from "react-i18next";

import L from "leaflet";
import Button from "@mui/material/Button";
import { MapContainer, TileLayer, useMap } from "react-leaflet";

import "leaflet/dist/leaflet.css";
import { getScale } from "../../utils/colorScales";
import Legend from "./Legend";
import useStore from "../../store";

const returnPeriods = [10, 15, 20, 25];

const HazardMap = () => {
  const { selectedCountry, selectedHazard } = useStore();
  const { t } = useTranslation();

  const [activeRPLayer, setActiveRPLayer] = useState(10);
  const [legendTitle, setLegendTitle] = useState("");
  const [mapInfo, setMapInfo] = useState({ geoJson: null, colorScale: null });
  const [percentileValues, setPercentileValues] = useState({});
  const [radius, setRadius] = useState(0);
  const [unit, setUnit] = useState("");

  const mapRef = useRef();

  const updateLegendTitle = (hazard, unit) => {
    const titles = {
      flood: `Flood depth${unit ? ` (${unit})` : ""}`,
      drought: `Standard Precipitation Index${unit ? ` (${unit})` : ""}`,
      heatwaves: `Warm Spell Duration Index${unit ? ` (${unit})` : ""}`,
    };
    return titles[hazard] || `Hazard${unit ? ` (${unit})` : ""}`;
  };

  useEffect(() => {
    setLegendTitle(updateLegendTitle(selectedHazard, unit));
  }, [selectedHazard, unit]);

  const fetchGeoJson = async () => {
    try {
      const tempPath = await window.electron.fetchTempDir();
      const response = await fetch(`${tempPath}/hazards_geodata.json`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setPercentileValues(data._metadata.percentile_values);
      setRadius(data._metadata.radius);
      setUnit(data._metadata.unit);

      if (
        data._metadata.percentile_values &&
        data._metadata.percentile_values[`rp${activeRPLayer}`]
      ) {
        const scale = getScale(
          selectedHazard,
          data._metadata.percentile_values[`rp${activeRPLayer}`]
        );
        setMapInfo({ geoJson: data, colorScale: scale });
      } else {
        throw new Error("Percentile values are missing or incomplete.");
      }
    } catch (error) {
      console.error("Error fetching GeoJSON data:", error);
      setMapInfo({ geoJson: null, colorScale: null });
    }
  };

  const CircleLayer = ({ data, colorScale }) => {
    const map = useMap();

    useEffect(() => {
      const layerGroup = L.layerGroup().addTo(map);

      data.features.forEach((feature) => {
        const { coordinates } = feature.geometry;
        const value = feature.properties[`rp${activeRPLayer}`];
        const country = feature.properties["country"];
        const name = feature.properties["name"];

        L.circle([coordinates[1], coordinates[0]], {
          color: colorScale(value),
          fillColor: colorScale(value),
          fillOpacity: 0.3,
          radius: radius,
        })
          .bindPopup(
            `${t("country")}: ${country}<br>${t("admin")} 2: ${name}<br>${t(
              "value"
            )}: ${value} ${unit}`
          )
          .addTo(layerGroup);
      });

      return () => layerGroup.clearLayers();
    }, [data, colorScale, map]);

    return null;
  };

  CircleLayer.propTypes = {
    data: PropTypes.shape({
      features: PropTypes.arrayOf(
        PropTypes.shape({
          geometry: PropTypes.shape({
            coordinates: PropTypes.arrayOf(PropTypes.number).isRequired,
          }).isRequired,
          properties: PropTypes.shape({
            [`rp${activeRPLayer}`]: PropTypes.number.isRequired,
            country: PropTypes.string.isRequired,
            name: PropTypes.string.isRequired,
          }).isRequired,
        }).isRequired
      ).isRequired,
    }).isRequired,
    colorScale: PropTypes.func.isRequired,
  };

  const handleRPLayerChange = async (rp) => {
    await fetchGeoJson();
    setActiveRPLayer(rp);
  };

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
    egypt: [26.8206, 30.8025],
    thailand: [15.87, 100.9925],
  };

  useEffect(() => {
    if (activeRPLayer !== null) {
      fetchGeoJson(activeRPLayer);
    }
  }, [activeRPLayer]);

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
        {returnPeriods.map((rp) => (
          <Button
            key={`rp-${rp}`}
            size="small"
            sx={RPButtonStyle(rp)}
            onClick={() => handleRPLayerChange(rp)}
            variant="contained"
          >
            {t("return_period")}
            {rp}
          </Button>
        ))}
      </div>
      {mapInfo.geoJson && mapInfo.colorScale && (
        <>
          <CircleLayer data={mapInfo.geoJson} colorScale={mapInfo.colorScale} />
          <Legend
            colorScale={mapInfo.colorScale}
            percentileValues={percentileValues ? percentileValues[`rp${activeRPLayer}`] : []}
            title={legendTitle}
          />
        </>
      )}
    </MapContainer>
  );
};

export default HazardMap;
