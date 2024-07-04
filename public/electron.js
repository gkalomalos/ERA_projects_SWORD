const { app, BrowserWindow, ipcMain } = require("electron");
const net = require("net");
const path = require("path");

global.pythonProcess = null;

const basePath = app.getAppPath();
let mainWindow;
let loaderWindow;

const pipeName = "\\\\.\\pipe\\electron-python-pipe";

const isDevelopmentEnv = () => {
  return !app.isPackaged;
};

if (!app.requestSingleInstanceLock()) {
  app.quit();
} else {
  app.on("second-instance", (event, commandLine, workingDirectory) => {
    // If second instance is instantiated, the app focuses on the current window.
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}

app.commandLine.appendSwitch("in-process-gpu");
if (app.getGPUFeatureStatus().gpu_compositing.includes("disabled")) {
  app.disableHardwareAcceleration();
}
app.whenReady().then(async () => {
  createLoaderWindow(); // Create the loader window
  global.pythonProcess = createPythonProcess();
  await waitForPythonProcessReady(global.pythonProcess); // Wait for the Python process to be ready
  loaderWindow.close(); // Close the loader window
  loaderWindow = null; // Clear the loader window reference
  createMainWindow(); // Create the main application window
});

const createLoaderWindow = () => {
  const iconPath = path.join(basePath, "build", "favicon.ico");

  loaderWindow = new BrowserWindow({
    height: 200,
    width: 300,
    center: true,
    alwaysOnTop: true,
    frame: false,
    resizable: false,
    autoHideMenuBar: true,
    icon: iconPath,
    webPreferences: {
      nodeIntegration: true,
    },
  });

  const loaderPath = path.join(basePath, "build", "loader.html");
  loaderWindow.loadFile(loaderPath);
};

const waitForPythonProcessReady = () => {
  return new Promise((resolve) => {
    const handleData = (data) => {
      const message = data.toString().trim();
      try {
        const event = JSON.parse(message);
        if (event.type === "event" && event.name === "ready") {
          global.pythonProcess.stdout.off("data", handleData);
          resolve();
        }
      } catch (error) {
        console.error("Error parsing Python stdout:", error);
      }
    };
    global.pythonProcess.stdout.on("data", handleData);
  });
};

const createMainWindow = () => {
  const iconPath = path.join(basePath, "build", "favicon.ico");

  mainWindow = new BrowserWindow({
    minHeight: 720,
    minWidth: 1280,
    frame: false,
    resizable: true,
    autoHideMenuBar: true,
    thickFrame: true,
    icon: iconPath,
    show: false,
    webPreferences: {
      contextIsolation: true,
      enableRemoteModule: false,
      preload: path.join(basePath, "build", "preload.js"),
      webSecurity: true,
      nodeIntegration: true,
    },
  });

  mainWindow.show();
  mainWindow.maximize();
  mainWindow.loadURL(`file://${path.join(basePath, "build", "index.html")}`);
  if (isDevelopmentEnv()) {
    mainWindow.webContents.openDevTools();
  }
};

const runPythonScript = (mainWindow, scriptName, data) => {
  return new Promise((resolve, reject) => {
    const client = net.connect({ path: pipeName, timeout: 300000 }, () => {
      const message = JSON.stringify({ scriptName, data });
      client.write(message);
    });

    let responseData = "";

    client.on("data", (data) => {
      responseData += data.toString();

      try {
        const response = JSON.parse(responseData);

        if (response.type === "progress") {
          mainWindow.webContents.send("progress-update", response);
          responseData = ""; // Reset responseData for next chunk
        } else if (response.success !== undefined) {
          client.end();
          if (response.success) {
            resolve(response.result);
          } else {
            reject(new Error(response.error));
          }
        }
      } catch (error) {
        if (!error.message.includes("Unexpected end of JSON input")) {
          console.error("Error parsing response data:", error);
          client.end();
          reject(error);
        }
      }
    });

    client.on("error", (error) => {
      console.error("Error with pipe connection:", error);
      reject(error);
    });

    client.on("end", () => {
      console.log("Pipe connection ended.");
    });
  });
};

// Create a long-running Python process
const createPythonProcess = () => {
  const scriptPath = path.join(basePath, "backend", "app.py");
  const pythonExecutable = path.join(basePath, "climada_env", "python.exe");

  try {
    const process = require("child_process").spawn(pythonExecutable, [scriptPath]);

    process.on("error", (error) => {
      console.error("Error occurred during Python process creation:", error);
    });

    process.stdout.on("data", (data) => {
      console.log("Python stdout:", data.toString());
    });

    process.stderr.on("data", (data) => {
      console.log("Python stderr:", data.toString());
    });

    return process;
  } catch (error) {
    console.error("Error occurred during Python process creation:", error);
    throw error;
  }
};

ipcMain.handle("runPythonScript", async (_, { scriptName, data }) => {
  try {
    const result = await runPythonScript(mainWindow, scriptName, data);
    return { success: true, result };
  } catch (error) {
    console.error(error);
    return { success: false, error: error.message };
  }
});

ipcMain.handle("is-development-env", () => {
  return !app.isPackaged;
});

ipcMain.handle("fetch-temp-dir", () => {
  const tempFolderPath = path.join(app.getAppPath(), "data", "temp");
  return tempFolderPath;
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

ipcMain.on("minimize", () => {
  mainWindow.minimize();
});

ipcMain.on("shutdown", () => {
  console.log("Shutting down application...");

  if (global.pythonProcess && !global.pythonProcess.killed) {
    global.pythonProcess.kill();
  }

  app.quit();
});

ipcMain.on("reload", () => {
  console.log("Reload CLIMADA App...");
  mainWindow.webContents.reloadIgnoringCache();
});

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.

app.on("activate", () => {
  // On OS X it's common to re-create a window in the app when the
  // dock icon is clicked and there are no other windows open.
  if (BrowserWindow.getAllWindows().length === 0) {
    createMainWindow();
  }
});

app.on("before-quit", () => {
  console.log("Terminating Python process before app quits...");

  if (global.pythonProcess && !global.pythonProcess.killed) {
    global.pythonProcess.kill();
  }
});
