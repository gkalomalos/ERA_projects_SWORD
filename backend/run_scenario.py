import json
import sys
from time import time

from cost_benefit import get_measures, get_measure_set
from handlers import (
    clear_temp_dir,
    initalize_data_directories,
    sanitize_country_name,
    set_map_title,
    update_progress,
)
from exposures import (
    generate_exposure_geojson,
    get_entity_from_xlsx,
    get_exposure,
    get_growth_exposure,
)
from hazard import generate_hazard_geojson, get_hazard, get_hazard_from_xlsx
from impact import calculate_impact, calculate_impact_function_set, generate_impact_geojson
from logger_config import LoggerConfig

logger = LoggerConfig(logger_types=["file"])

# Initialize data folder and subfolders if not exist
initalize_data_directories()


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

    adaptation_measures = request.get("adaptationMeasures", [])
    annual_population_growth = request.get("annualPopulationGrowth", 0)
    annual_gdp_growth = request.get("annualGDPGrowth", 0)
    country_name = request.get("countryName", "")
    exposure_economic = request.get("exposureEconomic", "")
    exposure_non_economic = request.get("exposureNonEconomic", "")
    hazard_type = request.get("hazardType", "")
    scenario = request.get("scenario", "")
    time_horizon = request.get("timeHorizon", "")

    country_name = sanitize_country_name(country_name)
    exposure_type = (
        exposure_economic if exposure_economic else exposure_non_economic
    )  # TODO: Needs redesign
    annual_growth = (
        annual_gdp_growth if exposure_economic else annual_population_growth
    )  # TODO: Needs redesign
    exposure_filename = request.get("exposureFile", "")
    hazard_filename = request.get("hazardFile", "")

    # Clear previously generated exposure/hazard/impact maps abd temp directory
    clear_temp_dir()

    try:
        # Generate exposure objects
        update_progress(20, "Generating Exposure object...")
        exposure_future = None
        if exposure_filename == "":
            # Get exposure data from API
            exposure_present = get_exposure(country_name)
            if annual_growth != 0:
                future_year = int(time_horizon)
                exposure_future = get_growth_exposure(exposure_present, annual_growth, future_year)
        else:
            # Get custom exposure data from xlsx file
            entity_present = get_entity_from_xlsx(exposure_filename)
            exposure_present = entity_present.exposures
            if annual_growth != 0:
                future_year = int(time_horizon)
                exposure_future = get_growth_exposure(exposure_present, annual_growth, future_year)

        # Generate geojson data files
        update_progress(30, "Generating Exposure geojson data files...")
        generate_exposure_geojson(exposure_present, country_name)

        # Generate hazard objects
        update_progress(40, "Generating Hazard object...")
        hazard_future = None
        if hazard_filename == "":
            hazard_present = get_hazard(hazard_type, scenario, time_horizon, country_name)
            if scenario != "historical":
                hazard_future = get_hazard(hazard_type, scenario, time_horizon, country_name)
        else:
            hazard_present = get_hazard_from_xlsx(hazard_filename)
            if scenario != "historical":
                # TODO: This needs refactoring. We need to decide on a process on how to
                #  handle future hazard data. For now, we are using the same hazard data
                hazard_future = get_hazard_from_xlsx(hazard_filename)

        # Generate Hazard geojson data files
        update_progress(50, "Generating Hazard geojson data files...")
        if scenario == "historical":
            generate_hazard_geojson(hazard_present, country_name)
        else:
            generate_hazard_geojson(hazard_future, country_name)

        # Calculate impact
        update_progress(60, "Generating Impact object...")

        # Calculate impact function. Same impact function set is used for both present and future
        impact_function_set = calculate_impact_function_set(hazard_present)

        # Calculate present impact
        impact_present = calculate_impact(exposure_present, hazard_present, impact_function_set)
        impact_future = None
        if scenario != "historical":
            impact_future = calculate_impact(exposure_present, hazard_future, impact_function_set)

        # Calculate impact geojson data files
        update_progress(70, "Generating Impact geojson data files...")
        if scenario == "historical":
            generate_impact_geojson(impact_present, country_name)
        else:
            generate_impact_geojson(impact_future, country_name)

        # Calculate adaptation measures
        if exposure_filename == "":
            measures = get_measures(hazard_present)
            measure_set = get_measure_set(measures=measures)
            pass
        else:
            measure_set = get_measure_set(exposure_filename)

        map_title = set_map_title(hazard_type, country_name, time_horizon, scenario)
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
