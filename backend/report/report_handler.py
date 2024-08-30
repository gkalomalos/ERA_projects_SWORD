import os
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import pandas as pd
import xlsxwriter

from constants import DATA_TEMP_DIR, REPORTS_DIR
from logger_config import LoggerConfig


@dataclass
class ReportParameters:
    annual_population_growth: Optional[str] = None
    annual_gdp_growth: Optional[str] = None
    country_code: Optional[str] = None
    country_name: Optional[str] = None
    exposure_economic: Optional[str] = None
    exposure_noneconomic: Optional[str] = None
    hazard: Optional[str] = None
    hazard_code: Optional[str] = None
    scenario: Optional[str] = None
    scenario_id: Optional[str] = None
    time_horizon: Optional[str] = None


@dataclass
class ReportViewObject:
    id: str
    data: dict
    image: str
    title: str
    type: str


class ReportHandler:
    def __init__(self, report_parameters: ReportParameters) -> None:
        self.report_parameters = report_parameters
        self.target_dir = REPORTS_DIR / self.report_parameters.scenario_id or DATA_TEMP_DIR
        report_file_path = self._get_report_file_path()
        self.workbook = xlsxwriter.Workbook(filename=report_file_path)
        self.logger = LoggerConfig(logger_types=["file"])

    def _get_report_file_path(self) -> str:
        country_code = self.report_parameters.country_code
        hazard_code = self.report_parameters.hazard_code
        exposure = (
            self.report_parameters.exposure_economic or self.report_parameters.exposure_noneconomic
        )
        # Construct the report file path within the target directory
        report_file_path = self.target_dir / f"{country_code}_{hazard_code}_{exposure}.xlsx"

        return str(report_file_path)

    def _generate_general_information_tab(self):
        ws = self.workbook.add_worksheet("General Information")

        # Hide gridlines
        ws.hide_gridlines(option=2)

        # Define formats
        bold_20_format = self.workbook.add_format({"bold": True, "font_size": 20})
        bold_11_format = self.workbook.add_format({"bold": True, "font_size": 11})
        normal_11_format = self.workbook.add_format({"font_size": 11})
        italic_11_format = self.workbook.add_format(
            {"italic": True, "font_size": 11, "align": "left"}
        )
        disclaimer_format = self.workbook.add_format(
            {"italic": True, "font_size": 11, "align": "left", "text_wrap": True}
        )

        # Input Fields Title
        ws.write("B2", "Input fields", bold_20_format)

        # Row 3 is empty
        ws.set_row(2, None, None)  # Row index is 2 (0-based)

        # Input Fields
        inputs = [
            ("B4", "Country", self.report_parameters.country_name),
            ("B5", "Hazard", self.report_parameters.hazard),
            ("B6", "Scenario", self.report_parameters.scenario),
            ("B7", "Time Horizon", self.report_parameters.time_horizon),
            ("B8", "Exposure of Economic Assets", self.report_parameters.exposure_economic or "-"),
            (
                "B9",
                "Exposure of Non-Economic Assets",
                self.report_parameters.exposure_noneconomic or "-",
            ),
            (
                "B10",
                "Annual Population Growth",
                (
                    f"{self.report_parameters.annual_population_growth}%"
                    if self.report_parameters.annual_population_growth
                    else "-"
                ),
            ),
            (
                "B11",
                "Annual GDP Growth",
                (
                    f"{self.report_parameters.annual_gdp_growth}%"
                    if self.report_parameters.annual_gdp_growth
                    else "-"
                ),
            ),
        ]

        for cell, label, value in inputs:
            ws.write(cell, label, bold_11_format)
            col_c_cell = cell.replace("B", "C")
            ws.write(col_c_cell, value, normal_11_format)

        # Report Created By
        ws.write("B14", "Report created by", bold_11_format)
        ws.write("B16", "User name", bold_11_format)
        ws.write("C16", os.getlogin(), normal_11_format)
        ws.write("B17", "Date", bold_11_format)
        ws.write("C17", datetime.now().strftime("%Y-%m-%d"), normal_11_format)
        ws.write("B18", "Time", bold_11_format)
        ws.write("C18", datetime.now().strftime("%H:%M:%S"), normal_11_format)

        # Disclaimer
        ws.write("B23", "Disclaimer:", italic_11_format)

        disclaimer = (
            "The user interface has been developed by GIZ and UNU-EHS/MCII to showcase the result of Enhancing Climate Risk Assessment (ERA) "
            "for Improved Country Risk Financing Strategies and allow users to explore CLIMADA tool for conducting climate risk analysis in Egypt "
            "and Thailand.\n"
            "The user interface is free software. You can redistribute and/or modify it. The installation and use of the user interface is done at "
            "the user's discretion and risk.\n"
            "The user agrees to be solely responsible for any damage to the computer system, loss of data or any other damage resulting from "
            "installation or use of the software.\n"
            "GIZ and UNU-EHS/MCII shall not be responsible or liable for any damages arising in connection with downloading, installation, modifying "
            "or any other use of the software.\n"
            "GIZ and UNU-EHS/MCII shall assume no responsibility for any errors or other mistakes or inaccuracies in the software, in the results "
            "produced by the software or in the related documentation.\n\n"
            "License for CLIMADA:\n"
            "Copyright (C) 2017 ETH Zurich, CLIMADA contributors listed in AUTHORS. CLIMADA is free software: you can redistribute it and/or modify "
            "it under the terms of the GNU General Public License Version 3, 29 June 2007 as published by the Free Software Foundation, https://www.gnu.org/licenses/gpl-3.0.html.\n"
            "CLIMADA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY "
            "or FITNESS FOR A PARTICULAR PURPOSE.\n"
            "See the GNU General Public License for more details: https://www.gnu.org/licenses/gpl-3.0.html."
        )

        ws.merge_range("B25:H35", disclaimer, disclaimer_format)

        # Set column width
        ws.set_column("B:B", 40)
        ws.set_column("C:C", 60)

    def _generate_hazard_tab(self):
        hazard_df = pd.read_parquet(self.target_dir / "hazard_report_data.parquet")

        ws = self.workbook.add_worksheet("Hazard")

        # Define a format for headers
        bold_format = self.workbook.add_format({"bold": True})

        # Write column headers with bold formatting
        for col_num, value in enumerate(hazard_df.columns):
            ws.write(0, col_num, value, bold_format)

        # Write data from DataFrame
        for row_num, row_data in enumerate(hazard_df.values.tolist(), start=1):
            for col_num, cell_data in enumerate(row_data):
                ws.write(row_num, col_num, cell_data)

    def _generate_exposure_tab(self):
        exposure_df = pd.read_parquet(self.target_dir / "exposure_report_data.parquet")

        ws = self.workbook.add_worksheet("Exposure")

        # Define a format for headers
        bold_format = self.workbook.add_format({"bold": True})

        # Write column headers with bold formatting
        for col_num, value in enumerate(exposure_df.columns):
            ws.write(0, col_num, value, bold_format)

        # Write data from DataFrame
        for row_num, row_data in enumerate(exposure_df.values.tolist(), start=1):
            for col_num, cell_data in enumerate(row_data):
                ws.write(row_num, col_num, cell_data)

    def _generate_impact_tab(self):
        impact_df = pd.read_parquet(self.target_dir / "impact_report_data.parquet")

        ws = self.workbook.add_worksheet("Impact")

        # Define a format for headers
        bold_format = self.workbook.add_format({"bold": True})

        # Write column headers with bold formatting
        for col_num, value in enumerate(impact_df.columns):
            ws.write(0, col_num, value, bold_format)

        # Write data from DataFrame
        for row_num, row_data in enumerate(impact_df.values.tolist(), start=1):
            for col_num, cell_data in enumerate(row_data):
                ws.write(row_num, col_num, cell_data)

    def _save_report(self):
        self.workbook.close()

    def generate_excel_report(self):
        self._generate_general_information_tab()
        self._generate_hazard_tab()
        self._generate_exposure_tab()
        self._generate_impact_tab()
        self._save_report()
