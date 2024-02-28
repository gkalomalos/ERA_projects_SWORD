import json
import sys
from time import time

from costben.costben_handler import CostBenefitHandler
from handlers import update_progress, beautify_hazard_type
from hazard.hazard_handler import HazardHandler
from logger_config import LoggerConfig


class RunFetchScenario:
    def __init__(self, request):
        self.request = request
        self.costben_handler = CostBenefitHandler()
        self.logger = LoggerConfig(logger_types=["file"])
        self.hazard_handler = HazardHandler()

    def run_fetch_measures(self) -> dict:
        initial_time = time()
        hazard_type = self.request.get("hazardType", "")
        hazard_code = self.hazard_handler.get_hazard_code(hazard_type)
        hazard_beautified = beautify_hazard_type(hazard_type)
        status_code = 2000

        measure_set = self.costben_handler.get_measure_set_from_excel(hazard_code)

        update_progress(10, "Fetching adaptation measures...")
        if not hazard_code or not measure_set:
            run_status_message = f"No available adaptation measures for {hazard_beautified}."
            adaptation_measures = []
            status_code = 3000
        else:
            run_status_message = (
                f"Fetched adaptation measures for {hazard_beautified} successfully."
            )
            adaptation_measures = measure_set.get_names(hazard_code)

        data = {"adaptationMeasures": adaptation_measures}

        update_progress(100, run_status_message)

        response = {
            "data": data,
            "status": {"code": status_code, "message": run_status_message},
        }

        # Clear files in temp directory
        self.logger.log(
            "info", f"Finished fetching adaptation measures data in {time() - initial_time}sec."
        )
        return response


if __name__ == "__main__":
    request = json.loads(sys.argv[1])
    runner = RunFetchScenario(request)
    response = runner.run_fetch_measures(request)
    print(json.dumps(response))
