import json
import sys
import os
import shutil
from time import time

from base_handler import BaseHandler
from logger_config import LoggerConfig

from constants import DATA_TEMP_DIR, REPORTS_DIR


class RunFetchReports:
    def __init__(self):
        self.base_handler = BaseHandler()
        self.logger = LoggerConfig(logger_types=["file"])

    def run_fetch_reports(self) -> None:
        initial_time = time()
        status_code = 2000

        self.base_handler.update_progress(10, "Fetching abailable data from reports directory...")

        try:
            
            ### ADD CODE HERE ###
            # Copy all files from DATA_TEMP_DIR to the destination directory
            # for item in os.listdir(DATA_TEMP_DIR):
            #     source_path = os.path.join(DATA_TEMP_DIR, item)
            #     destination_path = os.path.join(destination_dir, item)
            #     if os.path.isdir(source_path):
            #         shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
            #     else:
            #         shutil.copy2(source_path, destination_path)

            # self._create_disclaimer_file()
            run_status_message = "Fetched data from reports directory"
        except Exception as exc:
            run_status_message = (
                f"Error while trying to fetch data from reports directory. More info: {exc}"
            )
            status_code = 3000
            self.logger.log("error", run_status_message)

        self.base_handler.update_progress(100, run_status_message)

        response = {
            "data": {"data": {}},
            "status": {"code": status_code, "message": run_status_message},
        }

        self.logger.log(
            "info",
            f"Finished fetching data from reports directory in {time() - initial_time}sec.",
        )
        return response


if __name__ == "__main__":
    req = json.loads(sys.argv[1])
    runner = RunFetchReports(req)
    resp = runner.run_fetch_reports()
    print(json.dumps(resp))
