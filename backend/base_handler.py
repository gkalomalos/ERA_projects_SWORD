"""
Module to handle various utility functions and data processing tasks in the backend application.

This module provides a collection of functions to perform tasks such as checking CLIMADA API 
datasets, sanitizing country names, interpolating data, generating map titles, beautifying 
hazard types and scenarios, clearing temporary directories, initializing data directories, 
and updating progress for the frontend.
"""

import json
from os import makedirs, path
from pathlib import Path
import sys
from typing import Any, Dict, Optional

import geopandas as gpd
import pandas as pd
import pycountry

from climada.util.api_client import Client
from constants import (
    DATA_DIR,
    DATA_ENTITIES_DIR,
    DATA_EXPOSURES_DIR,
    DATA_HAZARDS_DIR,
    DATA_TEMP_DIR,
    LOG_DIR,
    REQUIREMENTS_DIR,
    REPORTS_DIR,
)
from logger_config import LoggerConfig

logger = LoggerConfig(logger_types=["file"])


class BaseHandler:
    """
    Generic class for handling basic data and app operations.
    """

    def check_data_type(self, country_name: str, data_type: str) -> list:
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

    def sanitize_country_name(self, country_name: str) -> str:
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

    def get_iso3_country_code(self, country_name: str) -> str:
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
                f"An error occurred while trying to convert country name to iso3. "
                f"More info: {exc}",
            )
            return None

    def set_map_title(
        self, hazard_type: str, country: str, time_horizon: str, scenario: str
    ) -> str:
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
        hazard_beautified = self.beautify_hazard_type(hazard_type)
        country_beautified = country.capitalize()
        scenario_beautified = self.beautify_scenario(scenario)

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

    def beautify_hazard_type(self, hazard_type: str) -> str:
        """
        Get a beautified version of the hazard type for UI and reports.

        This function returns a beautified string version of the hazard type to use in user
        interface elements and reports.

        :param hazard_type: The hazard type to search datasets for.
        :type hazard_type: str
        :return: The beautified string version of the hazard type.
        :rtype: str
        """
        _hazard_type = ""
        if hazard_type == "tropical_cyclone":
            _hazard_type = "Tropical cyclone"
        elif hazard_type == "storm_europe":
            _hazard_type = "Storm Europe"
        elif hazard_type == "river_flood":
            _hazard_type = "River flood"
        elif hazard_type == "drought":
            _hazard_type = "Drought"
        elif hazard_type == "flood":
            _hazard_type = "Flood"
        elif hazard_type == "heatwaves":
            _hazard_type = "Heatwaves"
        else:
            _hazard_type = "Hazard"

        return _hazard_type

    def beautify_scenario(self, scenario: str) -> str:
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

    def clear_temp_dir(self) -> None:
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

    def initalize_data_directories(self) -> None:
        """
        Initialize the data directories for the application.

        This function creates the necessary folders for storing data, including entities,
        exposures, hazards, logs, and temporary files. If the directories already exist,
        this function does nothing.

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
        if not path.exists(REPORTS_DIR):
            makedirs(REPORTS_DIR)

    def update_progress(self, progress: int, message: str) -> None:
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

    def get_admin_data(self, country_code: str, admin_level) -> gpd.GeoDataFrame:
        """
        Retrieve GeoDataFrame containing administrative boundary data for a specific country.

        This method reads the GeoJSON file containing administrative boundary data for the
        specified country and admin level. It returns the GeoDataFrame with necessary columns
        renamed for consistency.

        :param country_code: The ISO 3166-1 alpha-3 country code.
        :type country_code: str
        :param admin_level: The administrative level (e.g., 1 for country, 2 for regions).
        :type admin_level: int
        :return: GeoDataFrame containing administrative boundary data.
        :rtype: gpd.GeoDataFrame
        """
        try:
            file_path = REQUIREMENTS_DIR / f"gadm{admin_level}_{country_code}.geojson"
            admin_gdf = gpd.read_file(file_path)
            admin_gdf = admin_gdf[["shapeName", "shapeID", "shapeGroup", "geometry"]]
            admin_gdf = admin_gdf.rename(
                columns={
                    "shapeID": "id",
                    "shapeName": "name",
                    "shapeGroup": "country",
                }
            )
            return admin_gdf
        except FileNotFoundError:
            logger.log("error", f"File not found: {file_path}")
            return None
        except Exception as exception:
            logger.log(
                "error",
                f"An error occured while trying to get country admin level information. "
                f" More info: {exception}",
            )
            return None

    def create_results_metadata_file(self, metadata: Dict[str, str]) -> None:
        """
        Create a metadata file with column names in the first line and values in the second line.

        This method writes the provided metadata dictionary to a text file. The first line
        of the file contains the dictionary keys as column names, and the second line
        contains the corresponding values.

        :param metadata: A dictionary containing metadata where keys are the column names and values are the data entries.
        :type metadata: dict
        :return: None
        :rtype: None

        Example of metadata input dictionary:

        .. code-block:: python

            metadata = {
                "asset_type": "economic",
                "annual_growth": 2.5,
                "country_name": "thailand",
                "exposure_economic": "crops",
                "exposure_non_economic": "",
                "hazard_type": "heatwaves",
                "is_era": True,
                "scenario": "rcp45",
                "ref_year": 2024,
                "future_year": 2050,
                "app_option": "era"
            }
        """
        filepath = DATA_TEMP_DIR / "_metadata.txt"
        try:
            with open(filepath, "w") as file:
                # Write the column names
                file.write("\t".join(metadata.keys()) + "\n")
                # Write the values
                file.write("\t".join(map(str, metadata.values())) + "\n")
        except IOError as e:
            logger.log("error", (f"An I/O error occurred: {e.strerror}"))
        except Exception as e:
            logger.log("error", (f"An unexpected error occurred: {str(e)}"))

    def read_results_metadata_file(self) -> Dict[str, Any]:
        """
        Read the metadata file and return the metadata as a dictionary.

        This method reads a text file containing metadata where the first line contains the
        column names and the second line contains the corresponding values. The data is
        returned as a dictionary with appropriate type conversions.

        :return: A dictionary containing the metadata read from the file.
        :rtype: dict

        Example of returned metadata dictionary:

        .. code-block:: python

            {
                "asset_type": "economic",
                "annual_growth": 2.5,
                "country_name": "thailand",
                "exposure_economic": "crops",
                "exposure_non_economic": "",
                "hazard_type": "heatwaves",
                "is_era": True,
                "scenario": "rcp45",
                "ref_year": 2024,
                "future_year": 2050,
                "app_option": "era"
            }
        """
        filepath = DATA_TEMP_DIR / "_metadata.txt"
        metadata = {}

        try:
            with open(filepath, "r") as file:
                # Read the column names
                keys = file.readline().strip().split("\t")
                # Read the values
                values = file.readline().strip().split("\t")

                # Convert to dictionary
                metadata = dict(zip(keys, values))

                # Convert appropriate fields to their correct types
                metadata["annual_growth"] = float(metadata["annual_growth"])
                metadata["is_era"] = metadata["is_era"].lower() == "true"
                metadata["ref_year"] = int(metadata["ref_year"])
                metadata["future_year"] = int(metadata["future_year"])

        except IOError as e:
            logger.log("error", f"An I/O error occurred: {e.strerror}")
        except Exception as e:
            logger.log("error", f"An unexpected error occurred: {str(e)}")

        return metadata

    def check_file_type(self, file_path: Path) -> Optional[str]:
        """
        Check the type of the given file based on its extension.

        This method examines the file extension of the provided file path and determines
        whether the file is of a recognized type such as `.mat`, `.hdf5`, or `.tif`.

        :param file_path: The path to the file whose type is to be checked.
        :type file_path: Path

        :return: The file type as a string if recognized, otherwise None.
        :rtype: Optional[str]

        Example usage:

        .. code-block:: python

            file_type = file_handler.check_file_type(Path("data.hdf5"))
            if file_type:
                print(f"File is of type: {file_type}")
            else:
                print("File type is not recognized")
        """
        try:
            # Ensure the file exists before checking the type
            if not file_path.is_file():
                logger.log("error", f"File does not exist: {file_path}")
                return None

            # Extract the file extension
            _, file_extension = path.splitext(file_path)
            file_extension = file_extension.lower()

            # Define the recognized file types
            recognized_types = {
                ".mat": "mat",  # MATLAB file
                ".hdf5": "hdf5",  # HDF5 file
                ".h5": "hdf5",  # HDF5 file with .h5 extension
                ".tif": "raster",  # TIFF image file
                ".tiff": "raster",  # TIFF image file with .tiff extension
            }

            # Check if the file type is recognized
            if file_extension in recognized_types:
                return recognized_types[file_extension]
            else:
                logger.log("info", f"Unrecognized file type: {file_extension}")
                return None

        except Exception as e:
            logger.log("error", f"An unexpected error occurred: {str(e)}")
            return None

    def read_parquet_file(self, file_name: str) -> Optional[pd.DataFrame]:
        """
        Read a Parquet file from the DATA_TEMP_DIR directory.

        This method reads a Parquet file located in the `DATA_TEMP_DIR` directory and returns
        the contents as a pandas DataFrame.

        :param file_name: The name of the Parquet file to read.
        :type file_name: str

        :return: A pandas DataFrame if the file is successfully read, otherwise None.
        :rtype: Optional[pd.DataFrame]

        :raises FileNotFoundError: If the file does not exist in the DATA_TEMP_DIR directory.
        :raises ValueError: If the file extension is not `.parquet`.
        :raises Exception: For any other errors that occur during reading.

        Example usage:

        .. code-block:: python

            df = file_handler.read_parquet_file("data.parquet")
            if df is not None:
                print(df.head())
        """
        try:
            file_path = DATA_TEMP_DIR / file_name

            # Ensure the file exists
            if not file_path.is_file():
                raise FileNotFoundError(f"File does not exist: {file_path}")

            # Ensure the file has a .parquet extension
            if not file_path.suffix == ".parquet":
                raise ValueError(f"Incorrect file extension: {file_path.suffix}. Expected .parquet")

            # Read the Parquet file into a DataFrame
            df = pd.read_parquet(file_path)
            return df

        except FileNotFoundError as fnf_error:
            logger.log("error", str(fnf_error))
        except ValueError as ve:
            logger.log("error", str(ve))
        except Exception as e:
            logger.log("error", f"An unexpected error occurred while reading the file: {str(e)}")

        return None

    def save_parquet_file(self, df: pd.DataFrame, file_name: str) -> Optional[Path]:
        """
        Save a pandas DataFrame to a Parquet file in the DATA_TEMP_DIR directory.

        This method saves the provided DataFrame as a Parquet file in the `DATA_TEMP_DIR`
        directory.

        :param df: The DataFrame to save.
        :type df: pd.DataFrame

        :param file_name: The name of the file to save the DataFrame as, with a .parquet extension.
        :type file_name: str

        :return: The path to the saved Parquet file if successful, otherwise None.
        :rtype: Optional[Path]

        :raises ValueError: If the file extension is not `.parquet`.
        :raises Exception: For any other errors that occur during saving.

        Example usage:

        .. code-block:: python

            df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
            file_path = file_handler.save_parquet_file(df, "data.parquet")
            if file_path:
                print(f"DataFrame saved successfully at {file_path}")
        """
        try:
            # Ensure the file has a .parquet extension
            if not file_name.endswith(".parquet"):
                raise ValueError("The file name must end with .parquet")

            # Construct the full file path
            file_path = DATA_TEMP_DIR / file_name

            # Ensure the directory exists
            makedirs(DATA_TEMP_DIR, exist_ok=True)

            # Save the DataFrame to a Parquet file
            df.to_parquet(file_path, index=False, compression="snappy")
            return file_path

        except ValueError as ve:
            logger.log("error", str(ve))
        except Exception as e:
            logger.log("error", f"An unexpected error occurred while saving the file: {str(e)}")

        return None
