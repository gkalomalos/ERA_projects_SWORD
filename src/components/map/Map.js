import React, { useEffect, useState } from "react";

import { MapContainer, TileLayer, GeoJSON } from "react-leaflet";
import { scaleSequential } from "d3-scale";
import { interpolateRdYlGn } from "d3-scale-chromatic";
import "leaflet/dist/leaflet.css";

const Map = ({ activeMap }) => {
  const [mapInfo, setMapInfo] = useState({ geoJson: null, colorScale: null });
  const [activeLayer, setActiveLayer] = useState(1);

  useEffect(() => {
    const fetchGeoJson = async () => {
      try {
        const response = await fetch(
          `C:\\Users\\gkalomalos\\Projects\\unu\\climada-unu\\src\\components\\map\\${activeMap}_geodata_layer_${activeLayer}.json`
        );
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        const values = data.features.map((f) => f.properties.value);
        const minValue = Math.min(...values);
        const maxValue = Math.max(...values);
        const scale = scaleSequential(interpolateRdYlGn).domain([maxValue, minValue]);

        setMapInfo({ geoJson: data, colorScale: scale });
      } catch (error) {
        console.error("Error fetching GeoJSON data:", error);
        setMapInfo({ geoJson: null, colorScale: null });
      }
    };

    if (activeMap) {
      fetchGeoJson();
    }
  }, [activeMap]);

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

  const onEachFeature = (feature, layer) => {
    if (feature.properties) {
      layer.bindPopup(`Name: ${feature.properties.GID_1}<br>Value: ${feature.properties.value}`);
    }
  };

  return (
    <MapContainer center={[30.0, 31.0]} zoom={7} style={{ height: "100%", width: "100%" }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      {mapInfo.geoJson && mapInfo.colorScale && (
        <GeoJSON data={mapInfo.geoJson} style={style} onEachFeature={onEachFeature} />
      )}
    </MapContainer>
  );
};

export default Map;
