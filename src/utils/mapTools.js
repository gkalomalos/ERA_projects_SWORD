import L from "leaflet";
import "leaflet-simple-map-screenshoter";

export const takeScreenshot = (map, filePath) => {
  const screenshoter = L.simpleMapScreenshoter().addTo(map);
  screenshoter
    .takeScreen('blob')
    .then((blob) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64data = reader.result.split(',')[1];
        window.electron.saveScreenshot(base64data, filePath);
      };
      reader.readAsDataURL(blob);
    })
    .catch((e) => {
      console.error(e);
    });
};