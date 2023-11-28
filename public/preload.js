const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electron", {
  on: (channel, callback) => ipcRenderer.on(channel, callback),
  remove: (channel, callback) => ipcRenderer.removeListener(channel, callback),
  send: (channel, data) => ipcRenderer.send(channel, data),
  shutdown: () => ipcRenderer.send("shutdown"),
  isDevelopmentEnv: () => ipcRenderer.invoke("is-development-env"),
  fetchTempDir: () => ipcRenderer.invoke("fetch-temp-dir"),
});

contextBridge.exposeInMainWorld("api", {
  runPythonScript: async ({ scriptName, data }) => {
    return await ipcRenderer.invoke("runPythonScript", { scriptName, data });
  },
});
