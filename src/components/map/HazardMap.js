import React, { useEffect, useState, useRef } from "react";

import L from "leaflet";
import Button from "@mui/material/Button";
import { MapContainer, TileLayer, useMap } from "react-leaflet";
import { scaleSequential } from "d3-scale";
import { interpolateRdYlGn } from "d3-scale-chromatic";
import "leaflet/dist/leaflet.css";

const returnPeriods = [10, 50, 100, 250];

const HazardMap = ({ selectedCountry }) => {
  const [mapInfo, setMapInfo] = useState({ geoJson: null, colorScale: null });
  const [activeRPLayer, setActiveRPLayer] = useState(10);
  const mapRef = useRef();

  const fetchGeoJson = async () => {
    try {
      const tempPath = await window.electron.fetchTempDir();
      const response = await fetch(`${tempPath}/hazards_geodata.json`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      const values = data.features.map((f) => f.properties[`rp${activeRPLayer}`]);
      const minValue = Math.min(...values);
      const maxValue = Math.max(...values);
      const scale = scaleSequential(interpolateRdYlGn).domain([maxValue, minValue]);

      setMapInfo({ geoJson: data, colorScale: scale });
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
        const country = feature.properties["COUNTRY"];
        const name1 = feature.properties["NAME_1"];
        const name2 = feature.properties["NAME_2"];

        L.circle([coordinates[0], coordinates[1]], {
          color: colorScale(value),
          fillColor: colorScale(value),
          fillOpacity: 0.3,
          radius: 2000,
        })
          .bindPopup(
            `Country: ${country}<br>Admin 1: ${name1}<br>Admin 2: ${name2}<br>Value: ${value}`
          )
          .addTo(layerGroup);
      });

      return () => layerGroup.clearLayers();
    }, [data, colorScale, map]);

    return null;
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
    Egypt: [26.8206, 30.8025],
    Thailand: [15.87, 100.9925],
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
            RP{rp}
          </Button>
        ))}
      </div>
      {mapInfo.geoJson && mapInfo.colorScale && (
        <CircleLayer data={mapInfo.geoJson} colorScale={mapInfo.colorScale} />
      )}
    </MapContainer>
  );
};

export default HazardMap;
