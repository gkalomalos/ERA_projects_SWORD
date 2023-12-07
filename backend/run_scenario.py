from copy import deepcopy
import json
from os import makedirs, path
import sys
from time import time

import handlers
from constants import (
    DATA_EXPOSURES_DIR,
    DATA_HAZARDS_DIR,
    DATA_REPORTS_DIR,
    DATA_DIR,
    LOG_DIR,
    TEMP_DIR
)
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
if not path.exists(DATA_EXPOSURES_DIR):
    makedirs(DATA_EXPOSURES_DIR)
if not path.exists(DATA_HAZARDS_DIR):
    makedirs(DATA_HAZARDS_DIR)
if not path.exists(DATA_REPORTS_DIR):
    makedirs(DATA_REPORTS_DIR)
if not path.exists(LOG_DIR):
    makedirs(LOG_DIR)
if not path.exists(TEMP_DIR):
    makedirs(TEMP_DIR)


def run_scenario(request: dict) -> dict:
    """
    Run a scenario based on the given request and return the response.

    This function processes the request and runs the appropriate scenario, generates
    maps and plots, and creates .xlsx and .pdf reports for the scenario. It returns
    a dictionary containing the map title and status message.

    Parameters
    ----------
    request : dict
        A dictionary containing the necessary information for running the scenario,
        including keys such as "annualGrowth", "exposure", "hazard", "scenario",
        and "timeHorizon".

    Returns
    -------
    dict
        A dictionary containing the map title and status message, with keys "data" and "status".

    Example
    -------
    request = {
        "annualGrowth": 1.02,
        "exposure": {
            "file": "exposure_file.xlsx",
            "value": ["Country1", "Country2"],
        },
        "hazard": {
            "file": "hazard_file.hdf5",
            "value": "hazard_type",
        },
        "scenario": "historical",
        "timeHorizon": "2030",
    }
    response = run_scenario(request)
    """
    initial_time = time()
    annual_growth = request["annualGrowth"]
    country = request["country"]
    exposure_data = request["exposure"]
    hazard_data = request["hazard"]
    scenario = request["scenario"]
    time_horizon = request["timeHorizon"]

    exposure_filename = exposure_data["file"]
    hazard_filename = hazard_data["file"]

    # Clear previously generated exposure/hazard/impact maps abd temp directory
    handlers.clear_temp_dir()

    update_progress(10, "Setting up exposure...")
    # FLOW 1: User selects exposure and hazard.
    if exposure_filename == "" and hazard_filename == "":
        try:
            hazard_type = hazard_data["value"]
            exposure_present = handlers.get_exposure_new(country)
            update_progress(20, "Generating geojson data files")
            handlers.generate_exposure_geojson(exposure_present, country)

            update_progress(30, "Setting up hazard...")
            hazard_present = handlers.get_hazard_new(
                hazard_type, "historical", time_horizon, country
            )
            handlers.generate_hazard_geojson(
                hazard=hazard_present, country_name=country, intensity_thres=1
            )
            if scenario != "historical":
                hazard_future = handlers.get_hazard_new(
                    hazard_type, scenario, time_horizon, country
                )
                handlers.generate_hazard_geojson(
                    hazard=hazard_future, country_name=country, intensity_thres=1
                )

        except Exception as exception:
            status = {"code": 3000, "message": str(exception)}
            response = {"data": {"mapTitle": ""}, "status": status}
            return response

    # FLOW 2: User loads exposure and selects hazard.
    elif exposure_filename != "" and hazard_filename == "":
        try:
            hazard_type = hazard_data["value"]
            exposure_present = handlers.get_exposure_from_xlsx(
                path.join(DATA_EXPOSURES_DIR, exposure_filename)
            )
            update_progress(20, "Generating geojson data files")
            handlers.generate_hazard_geojson(
                hazard=hazard_present, country_name=country, intensity_thres=1
            )

            update_progress(30, "Setting up hazard...")
            handlers.generate_hazard_geojson(
                hazard=hazard_present, country_name=country, intensity_thres=1
            )
            if scenario != "historical":
                handlers.generate_hazard_geojson(
                    hazard=hazard_future, country_name=country, intensity_thres=1
                )
        except Exception as exception:
            status = {"code": 3000, "message": str(exception)}
            response = {"data": {"mapTitle": ""}, "status": status}
            return response

    # FLOW 3: User selects exposure and loads hazard.
    elif exposure_filename == "" and hazard_filename != "":
        h5_hazard_data = handlers.get_fields_from_hazard_file(hazard_filename)
        scenario = h5_hazard_data["scenario"]
        time_horizon = h5_hazard_data["time_horizon"]
        try:
            exposure_present = handlers.get_exposure(country)
            update_progress(20, "Generating geojson data files")
            handlers.generate_hazard_geojson(
                hazard=hazard_present, country_name=country, intensity_thres=1
            )

            update_progress(30, "Setting up hazard...")
            if scenario == "historical":
                hazard_present = handlers.get_hazard_from_hdf5(
                    path.join(DATA_HAZARDS_DIR, hazard_filename)
                )
                hazard_type = handlers.get_hazard_type_from_Hazard(hazard_present)
            else:
                hazard_future = handlers.get_hazard_from_hdf5(
                    path.join(DATA_HAZARDS_DIR, hazard_filename)
                )
                hazard_type = handlers.get_hazard_type_from_Hazard(hazard_future)
                hazard_present = handlers.get_hazard(
                    hazard_type, "historical", "1980_2020", country
                )
        except Exception as exception:
            status = {"code": 3000, "message": str(exception)}
            response = {"data": {"mapTitle": ""}, "status": status}
            return response

    # FLOW 4: User loads exposure and loads hazard.
    elif exposure_filename != "" and hazard_filename != "":
        h5_hazard_data = handlers.get_fields_from_hazard_file(hazard_filename)
        scenario = h5_hazard_data["scenario"]
        time_horizon = h5_hazard_data["time_horizon"]
        try:
            exposure_present = handlers.get_exposure_from_xlsx(
                path.join(DATA_EXPOSURES_DIR, exposure_filename)
            )
            update_progress(20, "Generating geojson data files")
            handlers.generate_exposure_geojson(exposure_present, country)

            update_progress(30, "Setting up hazard...")
            if scenario == "historical":
                hazard_present = handlers.get_hazard_from_hdf5(
                    path.join(DATA_HAZARDS_DIR, hazard_filename)
                )
                hazard_type = handlers.get_hazard_type_from_Hazard(hazard_present)
            else:
                hazard_future = handlers.get_hazard_from_hdf5(
                    path.join(DATA_HAZARDS_DIR, hazard_filename)
                )
                hazard_type = handlers.get_hazard_type_from_Hazard(hazard_future)
                hazard_present = handlers.get_hazard(
                    hazard_type, "historical", "1980_2020", country
                )
        except Exception as exception:
            status = {"code": 3000, "message": str(exception)}
            response = {"data": {"mapTitle": ""}, "status": status}
            return response
    update_progress(50, "Calculating impact...")

    # Calculate impact function
    impact_function_set = handlers.calculate_impact_function_set(
        hazard=hazard_present,
        impact_function_name="Flood Africa JRC Residential",  # TODO: Needs change
    )
    # Calculate present impact
    impact_present = handlers.calculate_impact(
        exposure=exposure_present,
        hazard=hazard_present,
        impact_function_set=impact_function_set,
    )
    handlers.generate_impact_geojson(impact_present, country)

    if scenario != "historical":
        # Cast annual growth to present exposure
        if annual_growth > 1:
            exposure_future = deepcopy(exposure_present)
            exposure_future.ref_year = handlers.get_ref_year(hazard_type, time_horizon)
            n_years = exposure_future.ref_year - exposure_present.ref_year + 1
            growth = annual_growth**n_years
            exposure_future.gdf["value"] = exposure_future.gdf["value"] * growth

            # Calculate future impact based on present exposure
            impact_future = handlers.calculate_impact(
                exposure=exposure_future,
                hazard=hazard_future,
                impact_function_set=impact_function_set,
            )
            handlers.generate_impact_geojson(impact_future, country)
        else:
            # Calculate future impact based on future exposure
            impact_future = handlers.calculate_impact(
                exposure=exposure_present,
                hazard=hazard_future,
                impact_function_set=impact_function_set,
            )
            handlers.generate_impact_geojson(impact_future, country)

    map_title = handlers.set_map_title(hazard_type, [country], time_horizon, scenario)
    run_status_message = f"Scenario run successfully."
    update_progress(100, run_status_message)
    response = {
        "data": {"mapTitle": map_title},
        "status": {"code": 2000, "message": run_status_message},
    }

    # Clear files in temp directory
    # handlers.clear_temp_dir()
    logger.log("debug", f"Finished running scenario in {time() - initial_time}sec.")
    return response


if __name__ == "__main__":
    request = json.loads(sys.argv[1])
    response = run_scenario(request)
    print(json.dumps(response))
