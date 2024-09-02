import React, { useState } from "react";

import ReportCard from "./ReportCard";
import useStore from "../../store";

const ReportsView = () => {
  const { reports, removeReport, updateReports } = useStore();

  const [selectedReport, setSelectedReport] = useState(null);

  const onCardClickHandler = (id) => {
    setSelectedReport((prevSelectedReport) => (prevSelectedReport === id ? null : id));
  };

  const onActionReportHandler = (id, action) => {
    const index = reports.findIndex((report) => report.id === id);
    if (action === "delete") {
      removeReport(id);
    } else if (action === "restore") {
      console.log("restored");
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
