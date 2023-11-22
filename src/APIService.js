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
  static async Test() {
    try {
      const scriptName = "run_test.py";
      const response = await window.api.runPythonScript({
        scriptName,
      });
      return response;
    } catch (error) {
      console.log(error);
    }
  }
}
