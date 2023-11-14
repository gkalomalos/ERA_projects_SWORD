const { app, BrowserWindow, ipcMain, protocol } = require("electron");
const { spawn } = require("child_process");
const path = require("path");

global.pythonProcess = null;

const basePath = app.getAppPath();
let mainWindow;
let loaderWindow;

const isDevelopmentEnv = () => {
  return process.env.NODE_ENV == "development";
};

if (!app.requestSingleInstanceLock()) {
  app.quit();
} else {
  app.on("second-instance", (event, commandLine, workingDirectory) => {
    // Someone tried to run a second instance, we should focus our window.
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });
}

const waitForPythonProcessReady = (pythonProcess) => {
  return new Promise((resolve) => {
    const handleData = (data) => {
      const message = data.toString().trim();
      try {
        const event = JSON.parse(message);
        if (event.type === "event" && event.name === "ready") {
          pythonProcess.stdout.off("data", handleData);
          resolve();
        }
      } catch (error) {
        console.error("Error parsing Python stdout:", error);
      }
    };
    pythonProcess.stdout.on("data", handleData);
  });
};

if (require("electron-squirrel-startup")) {
  app.quit();
}

app.commandLine.appendSwitch("in-process-gpu");
if (app.getGPUFeatureStatus().gpu_compositing.includes("disabled")) {
  app.disableHardwareAcceleration();
}
app.whenReady().then(async () => {
  // Register the custom protocol
  protocol.registerFileProtocol("static", (request, callback) => {
    const url = request.url.replace("static://", "");
    const filePath = isDevelopmentEnv()
      ? path.join(app.getAppPath(), "src", "assets", url)
      : path.join(process.resourcesPath, "assets", url);

    callback({ path: filePath });
  });

  createLoaderWindow(); // Create the loader window
  global.pythonProcess = createPythonProcess();
  await waitForPythonProcessReady(global.pythonProcess); // Wait for the Python process to be ready
  loaderWindow.close(); // Close the loader window
  loaderWindow = null; // Clear the loader window reference
  createMainWindow(); // Create the main application window
});

const createLoaderWindow = () => {
  const faviconPath = isDevelopmentEnv()
    ? path.join(basePath, "src", "assets", "favicon.ico")
    : path.join(process.resourcesPath, "assets", "favicon.ico");

  loaderWindow = new BrowserWindow({
    height: 200,
    width: 300,
    center: true,
    alwaysOnTop: true,
    frame: false,
    resizable: false,
    autoHideMenuBar: true,
    icon: faviconPath,
    webPreferences: {
      nodeIntegration: true,
    },
  });

  const loaderPath = isDevelopmentEnv()
    ? path.join(basePath, "src", "loader.html")
    : path.join(process.resourcesPath, "loader.html");
  loaderWindow.loadFile(loaderPath);
};

const createMainWindow = () => {
  const iconPath = isDevelopmentEnv()
    ? path.join(app.getAppPath(), "src", "assets", "favicon.ico")
    : path.join(process.resourcesPath, "assets", "favicon.ico");

  mainWindow = new BrowserWindow({
    minHeight: 720,
    minWidth: 1280,
    frame: true,
    resizable: true,
    autoHideMenuBar: true,
    thickFrame: true,
    icon: iconPath,
    show: false,
    webPreferences: {
      contextIsolation: true,
      enableRemoteModule: false,
      preload: MAIN_WINDOW_PRELOAD_WEBPACK_ENTRY,
      webSecurity: true,
      nodeIntegration: true,
    },
  });

  mainWindow.show();
  mainWindow.maximize();
  mainWindow.loadURL(MAIN_WINDOW_WEBPACK_ENTRY);
  if (isDevelopmentEnv()) {
    mainWindow.webContents.openDevTools();
  }
};

const runPythonScript = (mainWindow, scriptName, data) => {
  return new Promise((resolve, reject) => {
    let buffer = "";

    const message = {
      scriptName,
      data,
    };

    global.pythonProcess.stdin.write(JSON.stringify(message) + "\n");

    const handleData = (data) => {
      buffer += data.toString();
      let boundary = buffer.indexOf("\n");

      while (boundary !== -1) {
        const rawData = buffer.substring(0, boundary);
        buffer = buffer.substring(boundary + 1);

        if (rawData.trim().startsWith("{") || rawData.trim().startsWith("[")) {
          try {
            const response = JSON.parse(rawData);
            if (response.type === "progress") {
              mainWindow.webContents.send("progress", response);
            } else {
              global.pythonProcess.stdout.off("data", handleData);
              if (response.success) {
                resolve(response.result);
              } else {
                reject(new Error(response.error));
              }
            }
          } catch (error) {
            console.error("Error parsing Python stdout:", error);
            reject(error);
          }
        }

        boundary = buffer.indexOf("\n");
      }
    };

    global.pythonProcess.stdout.on("data", handleData);
  });
};

// Create a long-running Python process
const createPythonProcess = () => {
  const scriptPath = isDevelopmentEnv()
    ? path.join(basePath, "backend", "app.py")
    : path.join(process.resourcesPath, "backend", "app.py");
  const pythonExecutable = isDevelopmentEnv()
    ? path.join(basePath, "backend", "climada_env", "python.exe")
    : path.join(process.resourcesPath, "backend", "climada_env", "python.exe");

  try {
    const process = spawn(pythonExecutable, [scriptPath], {
      stdio: ["pipe", "pipe", "pipe", "ipc"],
    });

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

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
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
