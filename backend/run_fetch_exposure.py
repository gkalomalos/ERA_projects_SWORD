import json
import sys
from time import time

from logger_config import LoggerConfig

logger = LoggerConfig(logger_types=["file"])


def update_progress(progress, message):
    progress_data = {"type": "progress", "progress": progress, "message": message}
    print(json.dumps(progress_data))
    logger.log("debug", f"send progress {progress} to frontend.")
    sys.stdout.flush()


def run_fetch_exposure(request: dict) -> dict:
    initial_time = time()
    country_name = request["selectedCountry"]
    exposure_type = request["selectedExposureType"]

    run_status_message = f"Scenario run successfully."
    data = {"country_name": country_name, "exposure_type": exposure_type}
    update_progress(100, run_status_message)
    response = {
        "data": {"rData": data},
        "status": {"code": 2000, "message": run_status_message},
    }

    # Clear files in temp directory
    logger.log("debug", f"Finished fetching exposure in {time() - initial_time}sec.")
    return response


if __name__ == "__main__":
    request = json.loads(sys.argv[1])
    response = run_fetch_exposure(request)
    print(json.dumps(response))
