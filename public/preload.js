  const { contextBridge, ipcRenderer } = require("electron");

  contextBridge.exposeInMainWorld("electron", {
    fetchTempDir: () => ipcRenderer.invoke("fetch-temp-dir"),
    isDevelopmentEnv: () => ipcRenderer.invoke("is-development-env"),
    on: (channel, callback) => ipcRenderer.on(channel, callback),
    remove: (channel, callback) => ipcRenderer.removeListener(channel, callback),
    send: (channel, data) => ipcRenderer.send(channel, data),
  });

  contextBridge.exposeInMainWorld("api", {
    runPythonScript: async ({ scriptName, data }) => {
      return await ipcRenderer.invoke("runPythonScript", { scriptName, data });
    },
  });
