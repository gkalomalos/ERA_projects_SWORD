export default class APIService {
  static async Run(body) {
    try {
      const scriptName = "run_scenario.py";
      const response = await window.api.runPythonScript({
        scriptName,
        data: body,
      });
      return response;
    } catch (error) {
      console.log(error);
    }
  }

  static async CheckDataType(body) {
    try {
      const scriptName = "run_check_data_type.py";
      const response = await window.api.runPythonScript({
        scriptName,
        data: body,
      });
      return response;
    } catch (error) {
      console.log(error);
    }
  }

  static async FetchAdaptationMeasures(body) {
    try {
      const scriptName = "run_fetch_measures.py";
      const response = await window.api.runPythonScript({
        scriptName,
        data: body,
      });
      return response;
    } catch (error) {
      console.log(error);
    }
  }

  static async Shutdown() {
    try {
      const response = await window.electron.send("shutdown");
      return response;
    } catch (error) {
      console.log(error);
    }
  }

  static async Minimize() {
    try {
      const response = await window.electron.send("minimize");
      return response;
    } catch (error) {
      console.log(error);
    }
  }

  static async Refresh() {
    try {
      const response = await window.electron.send("reload");
      return response;
    } catch (error) {
      console.log(error);
    }
  }
}
