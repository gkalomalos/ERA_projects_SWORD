import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const Map = ({ mapData }) => {
  const [geoJson, setGeoJson] = useState(null);

  useEffect(() => {
    const fetchGeoJson = async () => {
      try {
        const response = await fetch(mapData);
        const data = await response.json();
        setGeoJson(data);
      } catch (error) {
        console.error("Error fetching GeoJSON data:", error);
      }
    };

    if (mapData) {
      fetchGeoJson();
    }
  }, [mapData]);

  return (
    <MapContainer
      center={[30.0, 31.0]}
      zoom={8}
      style={{ height: "100%", width: "100%" }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      {geoJson && <GeoJSON data={geoJson} />}
    </MapContainer>
  );
};

export default Map;
