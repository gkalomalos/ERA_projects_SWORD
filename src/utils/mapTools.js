import L from "leaflet";
import "leaflet-simple-map-screenshoter";
import useStore from "../store";

export const takeScreenshot = (map, filePath) => {
  const screenshoter = L.simpleMapScreenshoter().addTo(map);
  screenshoter
    .takeScreen("blob")
    .then((blob) => {
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64data = reader.result.split(",")[1];
        window.electron.saveScreenshot(base64data, filePath);
      };
      reader.readAsDataURL(blob);
    })
    .catch((e) => {
      console.error(e);
    });
};

// Listen for the save screenshot response
window.electron.onSaveScreenshotReply((event, { success, error }) => {
  const { setAlertMessage, setAlertSeverity, setAlertShowMessage } = useStore.getState();

  if (success) {
    setAlertMessage("Screenshot saved successfully!");
    setAlertSeverity("success");
  } else {
    setAlertMessage(`Failed to save screenshot: ${error}`);
    setAlertSeverity("error");
  }
  setAlertShowMessage(true);
});
