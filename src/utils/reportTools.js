import APIService from "../APIService";
import useStore from "../store";

export const fetchReports = async () => {
  const { addReport, setAlertMessage, setAlertSeverity, setAlertShowMessage } = useStore.getState();

  try {
    const response = await APIService.FetchReports();
    const { data, status } = response.result;

    if (status.code === 2000) {
      // Loop through each report and add it to the store
      data.forEach((report) => {
        const reportData = {
          id: report.id,
          data: report.data,
          data_dict: report.data_dict,
          image: report.image,
          title: report.title,
          type: report.type,
        };
        addReport(reportData);
      });

      setAlertMessage("Reports fetched and added successfully!");
      setAlertSeverity("success");
    } else {
      setAlertMessage(`Failed to fetch reports: ${status.message}`);
      setAlertSeverity("error");
    }
  } catch (error) {
    console.error("Error fetching reports:", error);
    setAlertMessage("An error occurred while fetching reports.");
    setAlertSeverity("error");
  } finally {
    setAlertShowMessage(true);
  }
};
