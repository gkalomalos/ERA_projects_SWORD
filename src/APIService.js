export default class APIService {
  static async FetchExposure(body) {
    try {
      const scriptName = "run_fetch_exposure.py";
      const response = await window.api.runPythonScript({
        scriptName,
        data: body,
      });
      return response;
    } catch (error) {
      console.log(error);
    }
  }

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
}
