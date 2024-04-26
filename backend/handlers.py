"""
Module to handle various utility functions and data processing tasks in the backend application.

This module provides a collection of functions to perform tasks such as checking CLIMADA API 
datasets, sanitizing country names, interpolating data, generating map titles, beautifying 
hazard types and scenarios, clearing temporary directories, initializing data directories, 
and updating progress for the frontend.

Functions:

check_data_type: 
    Checks if CLIMADA API offers a specific data type for a given country.
sanitize_country_name: 
    Sanitizes the input country name.
get_iso3_country_code: 
    Retrieves the ISO3 country code for a given country name.
get_interp1d_value: 
    Interpolates values for different return periods.
get_nearest_value: 
    Retrieves the nearest value in an array of numbers.
set_map_title: 
    Generates a map title for a specified scenario.
beautify_hazard_type:   
    Beautifies the hazard type string for UI and reports.
beautify_scenario: 
    Beautifies the scenario string for UI and reports.
clear_temp_dir: 
    Clears the temporary directory.
initialize_data_directories: 
    Initializes the data directories for the application.
update_progress: 
    Updates the progress and message for the frontend.
"""

import json
from os import makedirs, path
import sys
import pycountry

from climada.util.api_client import Client
from constants import (
    DATA_DIR,
    DATA_ENTITIES_DIR,
    DATA_EXPOSURES_DIR,
    DATA_HAZARDS_DIR,
    DATA_TEMP_DIR,
    LOG_DIR,
)
from logger_config import LoggerConfig

logger = LoggerConfig(logger_types=["file"])


def check_data_type(country_name: str, data_type: str) -> list:
    """
    Check if CLIMADA API offers the specified data type for the given country.

    This function queries the CLIMADA API to check if it offers the specified data type
    for the specified country. It returns a list of dataset information if available,
    otherwise returns an empty list.

    :param country_name: The name of the country to check.
    :type country_name: str
    :param data_type: The type of data to check.
    :type data_type: str
    :return: A list of dataset information if available, otherwise an empty list.
    :rtype: list
    """
    dataset_infos = []
    try:
        client = Client()
        dataset_infos = client.list_dataset_infos(
            data_type=data_type,
            properties={
                "country_name": country_name,
            },
        )
        return len(dataset_infos) > 0
    except Exception as exception:
        logger.log("error", f"An error has occurred. More info: {exception}")
        return False


def sanitize_country_name(country_name: str) -> str:
    """
    Sanitize the given country name.

    This function attempts to sanitize the provided country name by searching for a
    matching country using the `pycountry` library. If a match is found, it returns
    the standardized name of the country. If no match is found, it raises a ValueError.

    :param country_name: The name of the country to sanitize.
    :type country_name: str
    :return: The standardized name of the country.
    :rtype: str
    :raises ValueError: If the country name cannot be sanitized.
    """
    try:
        country = pycountry.countries.search_fuzzy(country_name)[0]
        return country.name
    except LookupError as exception:
        logger.log(
            "error",
            f"Error while trying to sanitize country name. More info: {exception}",
        )
        raise ValueError(
            f"Failed to sanitize country: {country_name}. More info: {exception}"
        ) from exception


def get_iso3_country_code(country_name: str) -> str:
    """
    Get the ISO3 country code for the given country name.

    This function attempts to retrieve the ISO3 country code for the provided country name
    using the `pycountry` library. If the country name is found, it returns the ISO3 code.
    If the country name is not found, it logs an error and returns None.

    :param country_name: The name of the country to get the ISO3 code for.
    :type country_name: str
    :return: The ISO3 country code.
    :rtype: str
    """
    try:
        country = pycountry.countries.search_fuzzy(country_name)[0]
        country_code = country.alpha_3
        return country_code
    except LookupError:
        logger.log(
            "error", f"No ISO3 code found for '{country_name}'. Please check the country name."
        )
        return None
    except Exception as exc:
        logger.log(
            "error",
            f"An error occurred while trying to convert country name to iso3. More info: {exc}",
        )
        return None


def set_map_title(hazard_type: str, country: str, time_horizon: str, scenario: str) -> str:
    """
    Generate the map title for the specified hazard, country, time horizon, and scenario.

    This function generates a map title to present in the user interface based on the specified
    hazard type, country, time horizon, and scenario.

    :param hazard_type: The type of hazard to search datasets for.
    :type hazard_type: str
    :param country: The name of the country.
    :type country: str
    :param time_horizon: The time horizon to search datasets.
    :type time_horizon: str
    :param scenario: The type of scenario to search datasets for.
    :type scenario: str
    :return: The map title for the specified scenario.
    :rtype: str
    """
    hazard_beautified = beautify_hazard_type(hazard_type)
    country_beautified = country.capitalize()
    scenario_beautified = beautify_scenario(scenario)

    if scenario == "historical":
        map_title = (
            f"{hazard_beautified} risk analysis for {country_beautified} "
            f"in {time_horizon} {scenario_beautified} scenario."
        )
    else:
        map_title = (
            f"{hazard_beautified} risk analysis for {country_beautified} "
            f"in {time_horizon} (scenario {scenario_beautified})."
        )
    return map_title


def beautify_hazard_type(hazard_type: str) -> str:
    """
    Get a beautified version of the hazard type for UI and reports.

    This function returns a beautified string version of the hazard type to use in user interface
    elements and reports.

    :param hazard_type: The hazard type to search datasets for.
    :type hazard_type: str
    :return: The beautified string version of the hazard type.
    :rtype: str
    """
    _hazard_type = ""
    if hazard_type == "tropical_cyclone":
        _hazard_type = "Tropical cyclone"
    if hazard_type == "storm_europe":
        _hazard_type = "Storm Europe"
    if hazard_type == "river_flood":
        _hazard_type = "River flood"
    if hazard_type == "drought":
        _hazard_type = "Drought"
    if hazard_type == "flood":
        _hazard_type = "Flood"

    return _hazard_type


def beautify_scenario(scenario: str) -> str:
    """
    Get a beautified version of the scenario for UI and reports.

    This function returns a beautified string version of the scenario to use in user interface
    elements and reports.

    :param scenario: The type of scenario to search datasets for.
    :type scenario: str
    :return: The beautified string version of the scenario.
    :rtype: str
    """
    _scenario = ""
    if scenario == "rcp26":
        _scenario = "RCP 2.6"
    if scenario == "rcp45":
        _scenario = "RCP 4.5d"
    if scenario == "rcp60":
        _scenario = "RCP 6.0"
    if scenario == "rcp85":
        _scenario = "RCP 8.5"
    if scenario == "historical":
        _scenario = "historical"

    return _scenario


def clear_temp_dir() -> None:
    """
    Clear the temporary directory.

    This function deletes all files in the temporary directory.

    :return: None
    """
    try:
        for file in DATA_TEMP_DIR.glob("*"):
            file.unlink(missing_ok=True)
    except Exception as exc:
        logger.log("error", f"Error while trying to clear temp directory. More info: {exc}")


def initalize_data_directories() -> None:
    """
    Initialize the data directories for the application.

    This function creates the necessary folders for storing data, including entities, exposures,
    hazards, logs, and temporary files. If the directories already exist, this function
    does nothing.

    :return: None
    """
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


def update_progress(progress: int, message: str) -> None:
    """
    Update the progress and message for the frontend.

    :param progress: An integer representing the progress value.
    :param message: A string containing the progress message.
    :return: None
    """
    progress_data = {"type": "progress", "progress": progress, "message": message}
    print(json.dumps(progress_data))
    logger.log("info", f"send progress {progress} to frontend.")
    sys.stdout.flush()
