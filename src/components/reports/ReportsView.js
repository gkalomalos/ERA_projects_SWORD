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

  return (
    <>
      <ReportCard
        data="Thailand/2050/SSP2-4.5/Flood/Markets/GDP2/..."
        id="1"
        image={image2}
        isSelected={selectedReport === "1"}
        onCardClick={onCardClickHandler}
        title="Flood Expansion – return period 1 in 100 years"
        type="Economic – Risk – Hazard – Map"
      />
      <ReportCard
        data="Thailand/2050/SSP2-4.5/Flood/Markets/GDP2/…"
        id="2"
        image={image3}
        isSelected={selectedReport === "2"}
        onCardClick={onCardClickHandler}
        title="Exposure of Markets"
        type="Economic – Risk – Exposure – Map "
      />
      <ReportCard
        data="Thailand/2050/SSP2-4.5/Flood/Markets/GDP2/..."
        id="3"
        image={image1}
        isSelected={selectedReport === "3"}
        onCardClick={onCardClickHandler}
        title="Cost-Benefit Analysis of Adaptation Measures"
        type="Economic – Adaptation – Cost-Benefit – Chart "
      />
    </>
  );
};

export default ReportsView;
