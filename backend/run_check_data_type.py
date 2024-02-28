import json
import sys
from time import time

from handlers import check_data_type, sanitize_country_name, update_progress
from logger_config import LoggerConfig


class RunCheckDataType:
    def __init__(self, request):
        self.request = request
        self.logger = LoggerConfig(logger_types=["file"])

    def run_check_data_type(self) -> dict:
        initial_time = time()
        country_name = self.request.get("country", "")
        country_name = sanitize_country_name(country_name)
        data_type = self.request.get("dataType", "")
        status_code = 2000

        update_progress(10, "Checking CLIMADA API")
        is_valid_data_type = check_data_type(country_name, data_type)

        if not is_valid_data_type:
            run_status_message = (
                f"No datasets available for {data_type} in {country_name} in CLIMADA's API."
            )
            data = {}
            status_code = 3000
        else:
            run_status_message = f"Fetched {data_type} data successfully."
            data = {}

        update_progress(100, run_status_message)

        response = {
            "data": {"data": data},
            "status": {"code": status_code, "message": run_status_message},
        }

        # Clear files in temp directory
        self.logger.log(
            "info", f"Finished fetching {data_type} data in {time() - initial_time}sec."
        )
        return response


if __name__ == "__main__":
    request = json.loads(sys.argv[1])
    runner = RunCheckDataType(request)
    response = runner.run_check_data_type(request)
    print(json.dumps(response))
