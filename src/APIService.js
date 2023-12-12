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

  static async Shutdown() {
    try {
      const response = await window.electron.send("shutdown");
      return response;
    } catch (error) {
      console.log(error);
    }
  }
}
