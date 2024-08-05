import L from "leaflet";
import "leaflet-simple-map-screenshoter";

export const takeScreenshot = (map) => {
  const screenshoter = L.simpleMapScreenshoter().addTo(map);
  screenshoter
    .takeScreen("blob")
    .then((blob) => {
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "map_screenshot.png";
      a.click();
      URL.revokeObjectURL(url);
    })
    .catch((e) => {
      console.error(e);
    });
};
