import React, { useState } from "react";

import { useReportTools } from "../../utils/reportTools";
import ReportCard from "./ReportCard";
import useStore from "../../store";

import APIService from "../../APIService";

const ReportsView = () => {
  const {
    reports,
    removeReport,
    setAlertMessage,
    setAlertSeverity,
    setAlertShowMessage,
    setSelectedScenarioRunCode,
    updateReports,
  } = useStore();
  const { restoreScenario } = useReportTools();

  const [selectedReport, setSelectedReport] = useState(null);

  const onCardClickHandler = (id) => {
    setSelectedReport((prevSelectedReport) => (prevSelectedReport === id ? null : id));
    setSelectedScenarioRunCode(id);
  };

  const onRemoveReportHandler = (code) => {
    const body = {
      code: code,
    };
    APIService.RemoveReport(body)
      .then((response) => {
        setAlertMessage(response.result.status.message);
        if (response.result.status.code === 2000) {
          setAlertSeverity("success");
          removeReport(code);
        } else {
          setAlertSeverity("error");
        }
        setAlertShowMessage(true);
      })
      .catch((error) => {
        console.log(error);
      });
  };

  const onActionReportHandler = (id, action) => {
    const index = reports.findIndex((report) => report.id === id);
    if (action === "delete") {
      onRemoveReportHandler(id);
    } else if (action === "restore") {
      restoreScenario(id);
    } else {
      const lastIndex = reports.length - 1;
      const [movedReport] = reports.splice(index, 1);
      let newIndex;
      if (action === "up") {
        newIndex = index === 0 ? lastIndex : index - 1;
      } else if (action === "down") {
        newIndex = index === lastIndex ? 0 : index + 1;
      }
      const newReportData = [...reports];
      newReportData.splice(newIndex, 0, movedReport);
      updateReports(newReportData);
    }
  };

  return (
    <>
      {reports.map((report) => (
        <ReportCard
          key={report.id}
          data={report.data}
          id={report.id}
          image={report.image}
          isSelected={selectedReport === report.id}
          onCardClick={onCardClickHandler}
          onReportAction={onActionReportHandler}
          title={report.title}
          type={report.type}
        />
      ))}
    </>
  );
};

export default ReportsView;
