from copy import deepcopy
import json
from os import makedirs, path
import sys
from time import time

from constants import (
    DATA_ENTITIES_DIR,
    DATA_EXPOSURES_DIR,
    DATA_HAZARDS_DIR,
    DATA_REPORTS_DIR,
    DATA_DIR,
    LOG_DIR,
    TEMP_DIR,
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
    annual_growth = request.get("annualGrowth", 0)  # TODO: Delete
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

    # # Clear previously generated exposure/hazard/impact maps abd temp directory
    handlers.clear_temp_dir()

    update_progress(10, "Setting up scenario parameters...")
    # FLOW 1: User selects exposure and hazard.
    if exposure_filename == "" and hazard_filename == "":
        try:
            update_progress(20, "Generating Exposure object...")
            exposure = handlers.get_exposure_new(country_name)
            # Cast annual growth to present exposure
            if annual_growth > 1:
                update_progress(30, "Cast annual growth to present Exposure object...")
                exposure_future = deepcopy(exposure)
                exposure_future.ref_year = handlers.get_ref_year(hazard_type, time_horizon)
                n_years = exposure_future.ref_year - exposure.ref_year + 1
                growth = annual_growth**n_years
                exposure_future.gdf["value"] = exposure_future.gdf["value"] * growth
                exposure = exposure_future

            update_progress(40, "Generating Exposure geojson data files...")
            handlers.generate_exposure_geojson(exposure, country_name)

            update_progress(50, "Generating Hazard object...")
            hazard = handlers.get_hazard_new(hazard_type, scenario, time_horizon, country_name)
            update_progress(60, "Generating Hazard geojson data files...")
            handlers.generate_hazard_geojson(hazard, country_name)
        except Exception as exception:
            status = {"code": 3000, "message": str(exception)}
            response = {"data": {"mapTitle": ""}, "status": status}
            return response

    # # FLOW 2: User loads exposure and selects hazard.
    # elif exposure_filename != "" and hazard_filename == "":
    #     try:
    #         hazard_type = hazard_data["value"]
    #         exposure_present = handlers.get_exposure_from_xlsx(
    #             path.join(DATA_EXPOSURES_DIR, exposure_filename)
    #         )
    #         update_progress(20, "Generating geojson data files")
    #         handlers.generate_hazard_geojson(hazard=hazard_present, country_name=country)

    #         update_progress(30, "Setting up hazard...")
    #         handlers.generate_hazard_geojson(hazard=hazard_present, country_name=country)
    #         if scenario != "historical":
    #             handlers.generate_hazard_geojson(hazard=hazard_future, country_name=country)
    #     except Exception as exception:
    #         status = {"code": 3000, "message": str(exception)}
    #         response = {"data": {"mapTitle": ""}, "status": status}
    #         return response

    # # FLOW 3: User selects exposure and loads hazard.
    # elif exposure_filename == "" and hazard_filename != "":
    #     h5_hazard_data = handlers.get_fields_from_hazard_file(hazard_filename)
    #     scenario = h5_hazard_data["scenario"]
    #     time_horizon = h5_hazard_data["time_horizon"]
    #     try:
    #         exposure_present = handlers.get_exposure(country)
    #         update_progress(20, "Generating geojson data files")
    #         handlers.generate_hazard_geojson(hazard=hazard_present, country_name=country)

    #         update_progress(30, "Setting up hazard...")
    #         if scenario == "historical":
    #             hazard_present = handlers.get_hazard_from_hdf5(
    #                 path.join(DATA_HAZARDS_DIR, hazard_filename)
    #             )
    #             hazard_type = handlers.get_hazard_type_from_Hazard(hazard_present)
    #         else:
    #             hazard_future = handlers.get_hazard_from_hdf5(
    #                 path.join(DATA_HAZARDS_DIR, hazard_filename)
    #             )
    #             hazard_type = handlers.get_hazard_type_from_Hazard(hazard_future)
    #             hazard_present = handlers.get_hazard(
    #                 hazard_type, "historical", "1980_2020", country
    #             )
    #     except Exception as exception:
    #         status = {"code": 3000, "message": str(exception)}
    #         response = {"data": {"mapTitle": ""}, "status": status}
    #         return response

    # # FLOW 4: User loads exposure and loads hazard.
    # elif exposure_filename != "" and hazard_filename != "":
    #     h5_hazard_data = handlers.get_fields_from_hazard_file(hazard_filename)
    #     scenario = h5_hazard_data["scenario"]
    #     time_horizon = h5_hazard_data["time_horizon"]
    #     try:
    #         exposure_present = handlers.get_exposure_from_xlsx(
    #             path.join(DATA_EXPOSURES_DIR, exposure_filename)
    #         )
    #         update_progress(20, "Generating geojson data files")
    #         handlers.generate_exposure_geojson(exposure_present, country)

    #         update_progress(30, "Setting up hazard...")
    #         if scenario == "historical":
    #             hazard_present = handlers.get_hazard_from_hdf5(
    #                 path.join(DATA_HAZARDS_DIR, hazard_filename)
    #             )
    #             hazard_type = handlers.get_hazard_type_from_Hazard(hazard_present)
    #         else:
    #             hazard_future = handlers.get_hazard_from_hdf5(
    #                 path.join(DATA_HAZARDS_DIR, hazard_filename)
    #             )
    #             hazard_type = handlers.get_hazard_type_from_Hazard(hazard_future)
    #             hazard_present = handlers.get_hazard(
    #                 hazard_type, "historical", "1980_2020", country
    #             )
    #     except Exception as exception:
    #         status = {"code": 3000, "message": str(exception)}
    #         response = {"data": {"mapTitle": ""}, "status": status}
    #         return response
    # update_progress(70, "Generating Impact object...")

    # Calculate impact function
    impact_function_set = handlers.calculate_impact_function_set(
        hazard=hazard,
        impact_function_name="Flood Africa JRC Residential",  # TODO: Needs change
    )
    # Calculate present impact
    impact = handlers.calculate_impact(exposure, hazard, impact_function_set)
    update_progress(80, "Generating Impact geojson data files...")
    handlers.generate_impact_geojson(impact, country_name)

    map_title = handlers.set_map_title(hazard_type, [country_name], time_horizon, scenario)

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
