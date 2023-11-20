import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const Map = ({ mapData }) => {
  const [geoData, setGeoData] = useState(null);

  useEffect(() => {
    if (mapData) {
      fetch(mapData)
        .then((response) => response.json())
        .then((data) => setGeoData(data))
        .catch((error) => console.error("Error loading GeoJSON:", error));
      console.log('mapData in map:', mapData)
    }
  }, [mapData]);

  // Function to determine the color based on a value
  const getColor = (value) => {
    // Define your color scale here
    return value > 1000
      ? "#800026"
      : value > 500
      ? "#BD0026"
      : value > 200
      ? "#E31A1C"
      : value > 100
      ? "#FC4E2A"
      : value > 50
      ? "#FD8D3C"
      : value > 20
      ? "#FEB24C"
      : value > 10
      ? "#FED976"
      : "#FFEDA0";
  };

  const styleFeature = (feature) => {
    return {
      fillColor: getColor(feature.properties.value),
      weight: 2,
      opacity: 1,
      color: "white",
      dashArray: "3",
      fillOpacity: 0.7,
    };
  };

  return (
    <MapContainer
      center={[30.0, 31.0]}
      zoom={8}
      style={{ height: "100%", width: "100%" }}
    >
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {geoData && <GeoJSON data={geoData} style={styleFeature} />}
    </MapContainer>
  );
};

export default Map;
