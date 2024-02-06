from copy import deepcopy
import json
from os import makedirs, path
import sys
from time import time

from constants import (
    DATA_ENTITIES_DIR,
    DATA_EXPOSURES_DIR,
    DATA_HAZARDS_DIR,
    DATA_DIR,
    LOG_DIR,
    DATA_TEMP_DIR,
)
import handlers
from logger_config import LoggerConfig

logger = LoggerConfig(logger_types=["file"])


def update_progress(progress, message):
    progress_data = {"type": "progress", "progress": progress, "message": message}
    print(json.dumps(progress_data))
    logger.log("debug", f"send progress {progress} to frontend.")
    sys.stdout.flush()


# Initialize data folder and subfolders if not exist
if not path.exists(DATA_DIR):
    makedirs(DATA_DIR)
if not path.exists(DATA_ENTITIES_DIR):
    makedirs(DATA_ENTITIES_DIR)
if not path.exists(DATA_EXPOSURES_DIR):
    makedirs(DATA_EXPOSURES_DIR)
if not path.exists(DATA_HAZARDS_DIR):
    makedirs(DATA_HAZARDS_DIR)
if not path.exists(LOG_DIR):
    makedirs(LOG_DIR)
if not path.exists(DATA_TEMP_DIR):
    makedirs(DATA_TEMP_DIR)


def run_scenario(request: dict) -> dict:
    """
    Run a scenario based on the provided request parameters.

    :param request: A dictionary containing the request parameters.
    :type request: dict
    :return: A dictionary containing the response data and status.
    :rtype: dict
    """
    initial_time = time()
    update_progress(10, "Setting up scenario parameters...")

    annual_population_growth = request.get("annualPopulationGrowth", 0)
    annual_gdp_growth = request.get("annualGDPGrowth", 0)
    country_name = request.get("countryName", "")
    exposure_economic = request.get("exposureEconomic", "")
    exposure_non_economic = request.get("exposureNonEconomic", "")
    hazard_type = request.get("hazardType", "")
    scenario = request.get("scenario", "")
    time_horizon = request.get("timeHorizon", "")

    country_name = handlers.sanitize_country_name(country_name)
    exposure_type = exposure_economic if exposure_economic else exposure_non_economic
    exposure_filename = request.get("exposureFile", "")
    hazard_filename = request.get("hazardFile", "")

    # Clear previously generated exposure/hazard/impact maps abd temp directory
    handlers.clear_temp_dir()

    try:
        # Generate exposure objects
        update_progress(20, "Generating Exposure object...")
        if exposure_filename == "":
            exposure_present = handlers.get_exposure(country_name)
        else:
            entity_present = handlers.get_entity_from_xlsx(exposure_filename)
            exposure_present = entity_present.exposures

        # Generate geojson data files
        update_progress(30, "Generating Exposure geojson data files...")
        handlers.generate_exposure_geojson(exposure_present, country_name)

        # Generate hazard objects
        update_progress(40, "Generating Hazard object...")
        if hazard_filename == "":
            hazard_present = handlers.get_hazard(hazard_type, scenario, time_horizon, country_name)
        else:
            hazard_present = handlers.get_hazard_from_xlsx(hazard_filename)

        # Generate Hazard geojson data files
        update_progress(50, "Generating Hazard geojson data files...")
        handlers.generate_hazard_geojson(hazard_present, country_name)

        # Calculate impact
        update_progress(60, "Generating Impact object...")

        # Calculate impact function
        impact_function_set = handlers.calculate_impact_function_set(hazard=hazard_present)

        # Calculate present impact
        impact_present = handlers.calculate_impact(
            exposure_present, hazard_present, impact_function_set
        )

        # Calculate impact geojson data files
        update_progress(70, "Generating Impact geojson data files...")
        handlers.generate_impact_geojson(impact_present, country_name)

        map_title = handlers.set_map_title(hazard_type, country_name, time_horizon, scenario)
    except Exception as exception:
        status = {"code": 3000, "message": str(exception)}
        response = {"data": {"mapTitle": ""}, "status": status}
        return response

    run_status_message = f"Scenario run successfully."
    update_progress(100, run_status_message)
    response = {
        "data": {"mapTitle": map_title},
        "status": {"code": 2000, "message": run_status_message},
    }
    logger.log("debug", f"Finished running scenario in {time() - initial_time}sec.")
    return response


if __name__ == "__main__":
    request = json.loads(sys.argv[1])
    response = run_scenario(request)
    print(json.dumps(response))
