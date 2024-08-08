import json
import sys
import os
import shutil
from time import time

from base_handler import BaseHandler
from logger_config import LoggerConfig

from constants import DATA_TEMP_DIR, REPORTS_DIR


class RunAddToOutput:
    def __init__(self, request):
        self.base_handler = BaseHandler()
        self.logger = LoggerConfig(logger_types=["file"])
        self.request = request

    def run_add_to_output(self) -> None:
        initial_time = time()
        status_code = 2000

        if not self.request:
            run_status_message = "Invalid request: Missing run scenario id"
            status_code = 3000
            self.logger.log("error", run_status_message)
            response = {
                "data": {"data": {}},
                "status": {"code": status_code, "message": run_status_message},
            }
            return response

        self.base_handler.update_progress(10, "Adding temp output data to reports directory...")

        try:
            # Define the destination directory
            destination_dir = REPORTS_DIR / self.request

            # Create the destination directory if it does not exist
            os.makedirs(destination_dir, exist_ok=True)

            # Copy all files from DATA_TEMP_DIR to the destination directory
            for item in os.listdir(DATA_TEMP_DIR):
                source_path = os.path.join(DATA_TEMP_DIR, item)
                destination_path = os.path.join(destination_dir, item)
                if os.path.isdir(source_path):
                    shutil.copytree(source_path, destination_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(source_path, destination_path)

            run_status_message = "Added temp output data to reports directory"
        except Exception as exc:
            run_status_message = (
                f"Error while trying to add temp output data to reports directory. More info: {exc}"
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
            f"Finished adding temp output data to reports directory in {time() - initial_time}sec.",
        )
        return response


if __name__ == "__main__":
    req = json.loads(sys.argv[1])
    runner = RunAddToOutput(req)
    resp = runner.run_add_to_output()
    print(json.dumps(resp))
