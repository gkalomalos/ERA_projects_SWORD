import React, { useEffect, useState } from "react";

import L from "leaflet";
import { MapContainer, TileLayer, GeoJSON, useMap } from "react-leaflet";
import { scaleSequential } from "d3-scale";
import { interpolateRdYlGn } from "d3-scale-chromatic";
import "leaflet/dist/leaflet.css";

const Map = ({ activeMap }) => {
  const [mapInfo, setMapInfo] = useState({ geoJson: null, colorScale: null });
  const [activeLayer, setActiveLayer] = useState("0"); // State to track the active layer

  // Mapping of layer names to specific numbers or strings
  const layerMapping = {
    "Admin level 0": "0",
    "Admin level 1": "1",
    "Admin level 2": "2",
  };

  const LayerControls = ({ layers }) => {
    const map = useMap();

    useEffect(() => {
      const control = L.control.layers(null, layers).addTo(map);

      // Modify DOM to change checkboxes to radio buttons and attach event listeners
      const layerControlElement = control.getContainer();
      const inputs = layerControlElement.getElementsByTagName("input");
      for (let i = 0; i < inputs.length; i++) {
        inputs[i].type = "radio";
        inputs[i].name = "leaflet-base-layers"; // Ensure all radios have the same name
        inputs[i].onchange = (e) => {
          const layerName = e.target.value;
          const mappedValue = layerMapping[layerName]; // Get the mapped value
          setActiveLayer(mappedValue); // Update active layer state with the mapped value
        };
      }

      // Set default layer (optional)
      if (inputs.length > 0) {
        inputs[0].checked = true;
        setActiveLayer(layerMapping[Object.keys(layers)[0]]); // Set initial active layer using mapping
      }

      return () => {
        control.remove();
      };
    }, [map, layers, layerMapping]);

    return null;
  };

  useEffect(() => {
    console.log("Active Layer:", activeLayer); // Log the active layer whenever it changes
  }, [activeLayer]);

  const layers = {
    "Admin level 0": L.layerGroup(),
    "Admin level 1": L.layerGroup(),
    "Admin level 2": L.layerGroup(),
  };

  useEffect(() => {
    const fetchGeoJson = async () => {
      try {
        // TODO: Change to dynamic
        const response = await fetch(
          `C:\\Users\\gkalomalos\\Projects\\unu\\climada-unu\\src\\components\\map\\${activeMap}_geodata_layer_${activeLayer}.json`
        );
        if (!response.ok) {
          // Check if the response is not ok (404 or other HTTP errors)
          throw new Error(`HTTP error! status: ${response.status}`); // Throw an error to go to the catch block
        }
        const data = await response.json();
        const values = data.features.map((f) => f.properties.value);
        const minValue = Math.min(...values);
        const maxValue = Math.max(...values);
        const scale = scaleSequential(interpolateRdYlGn).domain([maxValue, minValue]);

        setMapInfo({ geoJson: data, colorScale: scale });
      } catch (error) {
        console.error("Error fetching GeoJSON data for " + activeMap, error);
        setMapInfo({ geoJson: null, colorScale: null }); // Set to default state for empty map
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
    <MapContainer center={[27.5, 31.0]} zoom={7} style={{ height: "100%", width: "100%" }}>
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      {mapInfo.geoJson && mapInfo.colorScale && (
        <>
          <LayerControls layers={layers} />
          <GeoJSON data={mapInfo.geoJson} style={style} onEachFeature={onEachFeature} />
        </>
      )}
    </MapContainer>
  );
};

export default Map;
