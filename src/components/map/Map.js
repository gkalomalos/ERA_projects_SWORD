import React, { useEffect, useState, useRef } from "react";
import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const Map = ({ mapDataPath }) => {
  const position = [30.0, 31.0];
  const [geoJsonData, setGeoJsonData] = useState(null);
  const mapRef = useRef(null);

  useEffect(() => {
    if (mapDataPath) {
      fetch(mapDataPath)
        .then((response) => response.json())
        .then((data) => setGeoJsonData(data))
        .catch((error) => console.error('Error loading GeoJSON:', error));
    }
  }, [mapDataPath]);

  useEffect(() => {
    const map = mapRef.current;
    if (map && geoJsonData) {
      const geoJsonLayer = new L.GeoJSON(geoJsonData, {
        onEachFeature: (feature, layer) => {
          // Add popups or other feature-specific functionality
          if (feature.properties && feature.properties.value) {
            layer.bindPopup(`Value: ${feature.properties.value}`);
          }
        },
      });
      geoJsonLayer.addTo(map.leafletElement);
    }
  }, [geoJsonData]);

  return (
    <MapContainer
      center={position}
      zoom={8}
      style={{ height: "100%", width: "100%" }}
      ref={mapRef}
    >
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
    </MapContainer>
  );
};

export default Map;
