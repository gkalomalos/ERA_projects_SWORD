import React, { useEffect } from "react";
import L from "leaflet";
import { useMap } from "react-leaflet";

const Legend = ({ colorScale, position = "bottomright" }) => {
  const map = useMap();

  useEffect(() => {
    const legendControl = L.control({ position });

    legendControl.onAdd = function () {
      const div = L.DomUtil.create("div", "info legend");
      const grades = colorScale.domain(); // Ensure this is an array of grades for the legend

      div.innerHTML = `<svg width="20" height="200" style="margin: 10px 0 0 20px">
                        <defs>
                          <linearGradient id="gradient-${position}" x1="0%" y1="100%" x2="0%" y2="0%">
                            ${grades
                              .map(
                                (grade, index) =>
                                  `<stop offset="${((index / (grades.length - 1)) * 100).toFixed(
                                    0
                                  )}%" style="stop-color:${colorScale(grade)};stop-opacity:1" />`
                              )
                              .join("")}
                          </linearGradient>
                        </defs>
                        <rect x="0" y="0" width="20" height="200" style="fill: url(#gradient-${position});" />
                      </svg>
                      <div style="text-align: center;">
                        ${grades.map((grade) => `<div>${grade}</div>`).join("")}
                      </div>`;
      return div;
    };

    legendControl.addTo(map);

    return () => {
      legendControl.remove();
    };
  }, [colorScale, map, position]);

  return null;
};

export default Legend;
