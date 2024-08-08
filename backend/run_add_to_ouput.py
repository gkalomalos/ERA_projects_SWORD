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

    def _create_disclaimer_file(self):
        disclaimer_filepath = REPORTS_DIR / self.request / "_README.txt"

        # Disclaimer text
        disclaimer_text = """Disclaimer:
The user interface has been developed by GIZ and UNU-EHS/MCII to facilitate the sharing of Enhancing Climate Risk Assessment (ERA) project results from CLIMADA and allow users to explore CLIMADA functions.
The user interface is a free software. You can redistribute and/or modify it. The installation and use of the user interface is done at the user's discretion and risk.
The user agrees to be solely responsibility for any damage to the computer system, loss of data or any other damage resulting from installation or use of the software.
GIZ and UNU-EHS/MCII shall not be responsible or liable for any damages arising in connection with downloading, installation, modifying or any other use of the software.
GIZ and UNU-EHS/MCII shall assume no responsibility for any errors or other mistakes or inaccuracies in the software, in the results produced by the software or in the related documentation.

License for CLIMADA:
Copyright (C) 2017 ETH Zurich, CLIMADA contributors listed in AUTHORS. CLIMADA is free software: you can redistribute it and/or modify it under the terms of the
GNU General Public License Version 3, 29 June 2007 as published by the Free Software Foundation, https://www.gnu.org/licenses/gpl-3.0.html.
CLIMADA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details: https://www.gnu.org/licenses/gpl-3.0.html.
"""

        try:
            # Check if the file exists, if so, delete it
            if os.path.exists(disclaimer_filepath):
                os.remove(disclaimer_filepath)

            # Create and write the disclaimer text to the file
            with open(disclaimer_filepath, "w") as file:
                file.write(disclaimer_text)
        except IOError as e:
            self.logger.log(
                "error", f"An I/O error occurred while creating the disclaimer file: {e.strerror}"
            )
        except Exception as e:
            self.logger.log(
                "error",
                f"An unexpected error occurred while creating the disclaimer file: {str(e)}",
            )

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

            self._create_disclaimer_file()
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
