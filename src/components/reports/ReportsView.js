import React, { useState } from "react";

import image1 from "./cost_benefit_plot.png";
import image2 from "./risks_waterfall_plot_1.png";
import image3 from "./risks_waterfall_plot_2.png";

import ReportCard from "./ReportCard";

const ReportsView = () => {
  const [selectedReport, setSelectedReport] = useState(null);

  const onCardClickHandler = (id) => {
    setSelectedReport((prevSelectedReport) => (prevSelectedReport === id ? null : id));
  };

  // Test report data
  const reportData = [
    {
      id: "1",
      data: "Thailand/2050/SSP2-4.5/Flood/Markets/GDP2/...",
      image: image2,
      title: "Flood Expansion – return period 1 in 100 years",
      type: "Economic – Risk – Hazard – Map",
    },
    {
      id: "2",
      data: "Thailand/2050/SSP2-4.5/Flood/Markets/GDP2/…",
      image: image3,
      title: "Exposure of Markets",
      type: "Economic – Risk – Exposure – Map",
    },
    {
      id: "3",
      data: "Thailand/2050/SSP2-4.5/Flood/Markets/GDP2/...",
      image: image1,
      title: "Cost-Benefit Analysis of Adaptation Measures",
      type: "Economic – Adaptation – Cost-Benefit – Chart",
    },
  ];

  return (
    <>
      {reportData.map((report) => (
        <ReportCard
          key={report.id}
          data={report.data}
          id={report.id}
          image={report.image}
          isSelected={selectedReport === report.id}
          onCardClick={onCardClickHandler}
          title={report.title}
          type={report.type}
        />
      ))}
    </>
  );
};

export default ReportsView;
