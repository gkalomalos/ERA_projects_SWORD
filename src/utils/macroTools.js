import APIService from "../APIService";

import useStore from "../store";

export const useMacroTools = () => {
  const { setAlertMessage, setAlertSeverity, setAlertShowMessage, setCredOutputData } =
    useStore.getState();

  const loadCREDOutputData = () => {
    APIService.FetchCREDOutputData()
      .then((response) => {
        setAlertMessage(response.result.status.message);
        response.result.status.code === 2000
          ? setAlertSeverity("success")
          : setAlertSeverity("error");
        setCredOutputData(response.result.data);
      })
      .catch((error) => {
        setAlertShowMessage(true);
        console.log(error);
      });
  };

  return {
    loadCREDOutputData,
  };
};
