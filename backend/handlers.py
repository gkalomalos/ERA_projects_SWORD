"""
Module to handle various utility functions and data processing tasks in the backend application.

This module provides a collection of functions to perform tasks such as checking CLIMADA API 
datasets, sanitizing country names, interpolating data, generating map titles, beautifying 
hazard types and scenarios, clearing temporary directories, initializing data directories, 
and updating progress for the frontend.

Functions:
check_data_type: Checks if CLIMADA API offers a specific data type for a given country.
sanitize_country_name: Sanitizes the input country name.
get_iso3_country_code: Retrieves the ISO3 country code for a given country name.
get_interp1d_value: Interpolates values for different return periods.
get_nearest_value: Retrieves the nearest value in an array of numbers.
set_map_title: Generates a map title for a specified scenario.
beautify_hazard_type: Beautifies the hazard type string for UI and reports.
beautify_scenario: Beautifies the scenario string for UI and reports.
clear_temp_dir: Clears the temporary directory.
initialize_data_directories: Initializes the data directories for the application.
update_progress: Updates the progress and message for the frontend.

Author: [SWORD] Georgios Kalomalos
Email: georgios.kalomalos@sword-group.com
Date: 23/4/2024
"""

import json
from os import makedirs, path
import sys

import numpy as np
import pandas as pd
import pycountry

from climada.util.api_client import Client
from scipy.interpolate import interp1d
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
    Checks if CLIMADA API offers this data type for the specific country.
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
        logger.log("error", f"An error has occured. More info: {exception}")
        return False


def sanitize_country_name(country_name):
    try:
        country = pycountry.countries.search_fuzzy(country_name)[0]
        return country.name
    except LookupError as exception:
        logger.log(
            "error",
            f"Error while trying to sanitize country name. More info: {exception}",
        )
        raise ValueError(f"Failed to sanitize country name: {country_name}. More info: {exception}")


def get_iso3_country_code(country_name: str) -> str:
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


def get_interp1d_value(df: pd.DataFrame) -> float:
    """
    Get the interpolated value for different return periods.

    Parameters
    ----------
    df: pandas.DataFrame, required
        impact data DataFrame object.

    Returns
    -------
    interp1d_df: float
    """
    try:
        rpls = [1000, 750, 500, 400, 250, 200, 150, 100, 50, 10]
        interp1d_df = {"RP": rpls, "sum_loss": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}

        interp1d_df = pd.DataFrame(interp1d_df)

        if len(df) == 0:
            return interp1d_df

        if len(df) == 1:
            nearest_rp = get_nearest_value(interp1d_df["RP"].values, df["RP"].values)
            rp = df.iloc[0]["RP"]
            value = df.iloc[0]["sum_loss"]
            f = interp1d([0, rp], [0, value], fill_value="extrapolate")
            exp_value = f(nearest_rp)
            interp1d_df.loc[interp1d_df["RP"] == nearest_rp, "sum_loss"] = exp_value
            return interp1d_df

        rpl_high = get_nearest_value(np.array(rpls), df["RP"].max())
        rpl_low = get_nearest_value(np.array(rpls), df["RP"].min())

        if df["RP"].min() == 0:
            rpl_low = df.loc[df["sum_loss"] == 0, "RP"]

        # filter the rpl list
        rpls = list(filter(lambda x: x <= rpl_high and x >= rpl_low, rpls))
        for rpl in rpls:
            f = interp1d(df["RP"], df["sum_loss"], fill_value="extrapolate")
            value = f(rpl)
            interp1d_df.loc[interp1d_df["RP"] == rpl, "sum_loss"] = value

        # Replace negative sum_loss values with zeros
        interp1d_df[interp1d_df < 0] = 0
        return interp1d_df

    except Exception as exc:
        logger.log("error", f"Error while trying to interpolate values. More info: {exc}")
        return interp1d_df


def get_nearest_value(arr: list, value: float) -> float:
    """
    Get the nearest value in an array of numbers.

    Parameters
    ----------
    arr: list, required
        List of numbers.
    value: float, required
        Number for which to get the nearest value in the array of numbers.

    Returns
    -------
    float
    """
    index = np.abs(arr - value).argmin()
    return arr[index]


def set_map_title(hazard_type: str, country: str, time_horizon: str, scenario: str) -> str:
    """
    Generate the map title to present in the UI for the user specified scenario.

    Parameters
    ----------
    hazard_type: str, required
        Hazard type to search datasets.
        Example: river_flood, tropical_cyclone, storm_europe.
    countries: list, required
        List of country names for which to search for datasets.
        Example: ['Greece', 'Bulgaria', 'Slovenia']
    scenario: str, required
        Type of scenario to search datasets.
        Example: historical, rcp26, rcp45 etc.
    time_horizon: str, required
        Time horizon to search datasets.
        Example: 1980-2000, 2030-2050 etc.


    Returns
    -------
    map_title: str
        The map title for the user specified scenario.
    """
    hazard_beautified = beautify_hazard_type(hazard_type)
    country_beautified = country.capitalize()
    scenario_beautified = beautify_scenario(scenario)

    if scenario == "historical":
        map_title = f"{hazard_beautified} risk analysis for {country_beautified} in {time_horizon} {scenario_beautified} scenario."
    else:
        map_title = f"{hazard_beautified} risk analysis for {country_beautified} in {time_horizon} (scenario {scenario_beautified})."
    return map_title


def beautify_hazard_type(hazard_type: str) -> str:
    """
    Get a beautified version of the hazard type to use in UI and reports.

    Parameters
    ----------
    hazard_type: str, required
        Hazard type to search datasets.
        Example: river_flood, tropical_cyclone, storm_europe.

    Returns
    -------
    _hazard_type: str
        The beautified string version of the hazard type.
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
    Get a beautified version of the scenario to use in UI and reports.

    Parameters
    ----------
    scenario: str, required
        Type of scenario to search datasets.
        Example: historical, rcp26, rcp45 etc.

    Returns
    -------
    _scenario: str
        The beautified string version of the scenario.
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
    Clears the temporary directory.

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
    Initializes the data directories for the application.

    This function creates the necessary folders for storing data, including entities, exposures, hazards, logs, and temporary files.
    If the directories already exist, this function does nothing.

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
