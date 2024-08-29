import json
import sys
import os
from pathlib import Path
from time import time

from base_handler import BaseHandler
from report.report_handler import ReportViewObject
from logger_config import LoggerConfig
from constants import REPORTS_DIR

# Assuming these are paths to your static image assets
THAILAND_IMAGE_PATH = "/static/images/folder_grey_network_icon_512.png"
EGYPT_IMAGE_PATH = "/static/images/folder_grey_cloud_icon_512.png"


class RunFetchReports:
    def __init__(self):
        self.base_handler = BaseHandler()
        self.logger = LoggerConfig(logger_types=["file"])

    def run_fetch_reports(self) -> dict:
        initial_time = time()
        status_code = 2000

        self.base_handler.update_progress(10, "Fetching available data from reports directory...")

        reports = []  # List to store report objects
        try:
            # Iterate through each folder in REPORTS_DIR
            for report_dir in Path(REPORTS_DIR).iterdir():
                if report_dir.is_dir():
                    report_id = report_dir.name.split("_")[0]  # Extract ID from folder name

                    # Extract metadata or other relevant information
                    metadata = self.base_handler.read_results_metadata_file(report_dir)

                    # Generate title from directory name or metadata
                    title = report_dir.name

                    # Extract the country from the directory name
                    country_code = report_dir.name.split("_")[1].lower()

                    # Determine the image path based on the country code
                    if country_code == "tha":
                        image_path = THAILAND_IMAGE_PATH
                    elif country_code == "egy":
                        image_path = EGYPT_IMAGE_PATH
                    else:
                        image_path = ""  # Default or placeholder image

                    # Placeholder data dictionary, populate with actual extraction logic
                    data_dict = {}

                    # Assuming report_type is derived from metadata or directory name
                    report_type = "output_data"  # This can be dynamic

                    # Create a Report object
                    report = ReportViewObject(
                        id=report_id,
                        data=f"",
                        data_dict=metadata,
                        image=image_path,
                        title=title,
                        type=report_type,
                    )

                    reports.append(report)

            run_status_message = "Fetched data from reports directory"
        except Exception as exc:
            run_status_message = (
                f"Error while trying to fetch data from reports directory. More info: {exc}"
            )
            status_code = 3000
            self.logger.log("error", run_status_message)

        self.base_handler.update_progress(100, run_status_message)

        response = {
            "data": [report.__dict__ for report in reports],  # Convert Report objects to dict
            "status": {"code": status_code, "message": run_status_message},
        }

        self.logger.log(
            "info", f"Finished fetching data from reports directory in {time() - initial_time}sec."
        )
        return response


if __name__ == "__main__":
    req = json.loads(sys.argv[1])
    runner = RunFetchReports(req)
    resp = runner.run_fetch_reports()
    print(json.dumps(resp))
