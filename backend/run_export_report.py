"""
"""

import json
import sys
from time import time

from base_handler import BaseHandler
from hazard.hazard_handler import HazardHandler
from logger_config import LoggerConfig
from report.report_handler import ReportHandler, ReportParameters


class RunExportReport:
    def __init__(self, request):
        self.base_handler = BaseHandler()
        self.hazard_handler = HazardHandler()
        self.logger = LoggerConfig(logger_types=["file"])
        self.request = request

    def run_export_report(self) -> dict:
        initial_time = time()

        if not self.valid_request():
            run_status_message = "Invalid request: Missing required fields"
            status_code = 3000
            self.logger.log("error", run_status_message)
            response = {
                "data": {"data": {}},
                "status": {"code": status_code, "message": run_status_message},
            }
            return response

        export_type = self.request.get("exportType", "")
        scenario_code = self.request.get("scenarioRunCode", "")
        status_code = 2000

        self.base_handler.update_progress(20, "Generating excel report...")

        scenario_metadata = self.base_handler.get_scenario_metadata(scenario_code)
        report_parameters = ReportParameters(
            country_code=self.base_handler.get_iso3_country_code(
                scenario_metadata.get("country_name")
            ),
            country_name=scenario_metadata.get("country_name"),
            hazard=scenario_metadata.get("hazard_type"),
            hazard_code=self.hazard_handler.get_hazard_code(scenario_metadata.get("hazard_type")),
            scenario=scenario_metadata.get("scenario"),
            scenario_id=scenario_code,
            time_horizon=f"{scenario_metadata.get('ref_year')} - {scenario_metadata.get('future_year')}",
            exposure_economic=scenario_metadata.get("exposure_economic"),
            exposure_noneconomic=scenario_metadata.get("exposure_non_economic"),
            annual_population_growth=(
                scenario_metadata.get("annual_growth")
                if scenario_metadata.get("asset_type") == "economic"
                else None
            ),
            annual_gdp_growth=(
                scenario_metadata.get("annual_growth")
                if scenario_metadata.get("asset_type") == "non_economic"
                else None
            ),
        )

        report_handler = ReportHandler(report_parameters)
        report_handler.generate_excel_report()

        run_status_message = "Generated excel report successfully."
        self.base_handler.update_progress(100, run_status_message)

        response = {
            "data": {"data": {}},
            "status": {"code": status_code, "message": run_status_message},
        }

        self.logger.log("info", f"Finished generating excel report in {time() - initial_time}sec.")
        return response

    def valid_request(self) -> bool:
        """
        Validate the request data to ensure required fields are present.

        This method checks if the required fields are present in the request data.

        :return: True if the request is valid, False otherwise.
        :rtype: bool
        """
        required_fields = ["exportType", "scenarioRunCode"]
        for field in required_fields:
            if field not in self.request:
                self.logger.log("error", f"Missing required field: {field}")
                return False
        return True


if __name__ == "__main__":
    req = json.loads(sys.argv[1])
    runner = RunExportReport(req)
    resp = runner.run_export_report()
    print(json.dumps(resp))
