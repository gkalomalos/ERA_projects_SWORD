"""
Module to handle the fetching of report data from a specified directory.

This module provides functionality to retrieve report data from a specified directory,
process the data, and return it in a structured format. It contains a class and methods 
to fetch available reports, process metadata, and prepare response data.

Classes:

RunFetchReports:
    Handles the fetching and processing of report data from the specified reports directory.

Methods:

run_fetch_reports:
    Entry point to fetch and process report data, returning it as a structured response.
"""

import json
import sys
from pathlib import Path
from time import time

from base_handler import BaseHandler
from report.report_handler import ReportViewObject
from logger_config import LoggerConfig
from constants import REPORTS_DIR


class RunFetchReports:
    """
    Class for handling the fetching and processing of report data from the reports directory.

    This class provides functionality to iterate through report directories, extract relevant
    metadata, create report objects, and generate a response containing the processed report data.
    """

    def __init__(self):
        """
        Initialize the RunFetchReports instance.

        This initializes the BaseHandler and LoggerConfig instances required for handling
        operations and logging within the report fetching process.
        """
        self.base_handler = BaseHandler()
        self.logger = LoggerConfig(logger_types=["file"])

    def run_fetch_reports(self) -> dict:
        """
        Run the process to fetch report data from the reports directory.

        This method iterates through the directories within the reports directory, processes
        each directory to extract metadata and create report objects, and compiles the results
        into a structured response.

        :return: A dictionary containing the response data and status.
        :rtype: dict
        """
        initial_time = time()
        status_code = 2000

        self.base_handler.update_progress(10, "Fetching available data from reports directory...")

        reports = []  # List to store report objects
        try:
            # Iterate through each folder in REPORTS_DIR
            for report_dir in Path(REPORTS_DIR).iterdir():
                if report_dir.is_dir():
                    # Extract ID from folder name
                    report_id = report_dir.name

                    # Extract metadata from the _metadata.txt file
                    metadata = self.base_handler.read_results_metadata_file(
                        report_dir / "_metadata.txt"
                    )

                    # Generate title from directory name or metadata
                    title = report_dir.name

                    # Placeholder image path (can be updated based on actual data)
                    image_path = ""

                    # Assuming report_type is derived from metadata or directory name
                    report_type = "output_data"  # This can be dynamic

                    # Create a Report object
                    report = ReportViewObject(
                        id=report_id,
                        data=metadata,
                        image=image_path,
                        title=title,
                        type=report_type,
                    )

                    reports.append(report)

            run_status_message = "Fetched data from reports directory successfully."
        except Exception as exc:
            # Handle any exceptions that occur during the report fetching process
            run_status_message = (
                f"Error while trying to fetch data from reports directory. More info: {exc}"
            )
            status_code = 3000
            self.logger.log("error", run_status_message)

        self.base_handler.update_progress(100, run_status_message)

        # Prepare the response with the fetched report data
        response = {
            "data": [report.__dict__ for report in reports],  # Convert Report objects to dict
            "status": {"code": status_code, "message": run_status_message},
        }

        self.logger.log(
            "info",
            f"Finished fetching data from reports directory in {time() - initial_time:.2f} sec.",
        )
        return response


if __name__ == "__main__":
    req = json.loads(sys.argv[1])
    runner = RunFetchReports()
    resp = runner.run_fetch_reports()
    print(json.dumps(resp))
