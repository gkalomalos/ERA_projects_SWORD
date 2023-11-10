export default class APIService {
  static async Run(body) {
    try {
      const baseUrl =
        process.env.REACT_APP_BACKEND_URL || "http://localhost:8080";
      const response = await fetch(`${baseUrl}/api/run`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });
      return await response.json();
    } catch (error) {
      return console.log(error);
    }
  }
}
