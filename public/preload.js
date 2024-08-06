const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electron", {
  fetchTempDir: () => ipcRenderer.invoke("fetch-temp-dir"),
  isDevelopmentEnv: () => ipcRenderer.invoke("is-development-env"),
  on: (channel, callback) => ipcRenderer.on(channel, callback),
  remove: (channel, callback) => ipcRenderer.removeListener(channel, callback),
  send: (channel, data) => ipcRenderer.send(channel, data),
  saveScreenshot: (blob, filePath) => ipcRenderer.invoke("save-screenshot", { blob, filePath }),
  onSaveScreenshotReply: (callback) => ipcRenderer.on("save-screenshot-reply", callback),
});

contextBridge.exposeInMainWorld("api", {
  runPythonScript: async ({ scriptName, data }) => {
    return await ipcRenderer.invoke("runPythonScript", { scriptName, data });
  },
});
