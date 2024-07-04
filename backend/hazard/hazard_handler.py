"""
Module for handling hazard-related operations.

This module contains classes and functions for handling various types of hazards, such as 
tropical cyclones, river floods, earthquakes, wildfires, floods, and droughts. It includes
methods for fetching hazard data from different sources, processing hazard datasets, 
and generating hazard GeoJSON files.

Classes:

- `HazardHandler`: 
    Class for handling hazard-related operations.

Methods:

- `get_hazard_time_horizon`: 
    Retrieves the time horizon for a given hazard type, scenario, and time horizon.
- `get_hazard_dataset_properties`: 
    Retrieves hazard dataset properties based on hazard type, scenario, time horizon, and country.
- `get_hazard`: 
    Retrieves hazard data based on various parameters, including hazard type, 
    source, scenario, time horizon, country, and file path.
- `_get_hazard_from_client`: 
    Retrieves hazard data from an external API client.
- `_get_hazard_from_raster`: 
    Retrieves hazard data from a raster file.
- `_get_hazard_from_mat`: 
    Retrieves hazard data from a MATLAB file.
- `get_hazard_intensity_thres`: 
    Retrieves the intensity threshold for a given hazard type.
- `get_circle_radius`: 
    Retrieves the radius for generating hazard circles.
- `generate_hazard_geojson`: 
    Generates a GeoJSON file containing hazard data.
- `_get_hazard_from_hdf5`: 
    Retrieves hazard data from an HDF5 file.
- `get_hazard_from_xlsx`: 
    Retrieves hazard data from an Excel file.
- `get_hazard_code`: 
    Retrieves the hazard code corresponding to a given hazard type.
- `get_hazard_type`: 
    Retrieves the hazard type corresponding to a given hazard code.
"""

import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

from climada.hazard import Hazard
from climada.util.api_client import Client

from base_handler import BaseHandler
from constants import (
    DATA_HAZARDS_DIR,
    DATA_TEMP_DIR,
)
from logger_config import LoggerConfig

logger = LoggerConfig(logger_types=["file"])


class HazardHandler:
    """
    Class for handling hazard-related operations.

    This class provides methods for retrieving hazard data from various sources, processing
    hazard datasets, and generating hazard GeoJSON files.
    """

    def __init__(self, pipe):
        self.client = Client()
        self.base_handler = BaseHandler(pipe)

    # TODO: Needs to be refactored
    def get_hazard_time_horizon(self, hazard_type: str, scenario: str, time_horizon: str) -> str:
        """
        Get the time horizon for a specific hazard type and scenario.

        This method retrieves the time horizon for a specified hazard type and scenario.
        It uses predefined mappings for historical data and future projections. If the scenario
        is historical, it returns the corresponding time horizon from the historical dataset.
        For future scenarios, it maps the time horizon based on the hazard type and provided
        time horizon. If no match is found, it returns an empty string.

        :param hazard_type: The type of hazard for which to retrieve the time horizon.
        :type hazard_type: str
        :param scenario: The scenario type, either "historical" or "future".
        :type scenario: str
        :param time_horizon: The time horizon for future scenarios.
        :type time_horizon: str
        :return: The time horizon corresponding to the specified hazard type and scenario.
        :rtype: str
        """
        try:
            historical_time_horizons = {
                "storm_europe": "1940_2014",
                "river_flood": "1980_2000",
                "tropical_cyclone": "1980_2000",
                "earthquake": "",
                "flood": "2002_2019",
                "wildfire": "2001_2020",
            }

            tropical_cyclone_future_mapping = {
                "2010_2030": "2020",
                "2030_2050": "2040",
                "2050_2070": "2060",
                "2070_2090": "2080",
            }

            # Check if the scenario is historical
            if scenario == "historical":
                # Return the time horizon for historical scenarios, if available for the
                # given hazard type
                return historical_time_horizons.get(hazard_type, "")

            # Check if the hazard type is river flood
            if hazard_type == "river_flood":
                # Return the provided time horizon for river flood hazards
                return time_horizon

            # Check if the hazard type is tropical cyclone
            if hazard_type == "tropical_cyclone":
                # Return the mapped time horizon for future tropical cyclone scenarios,
                # if available
                return tropical_cyclone_future_mapping.get(time_horizon, "")

            # Default return if no match found
            return ""

        except Exception as exception:
            logger.log(
                "error",
                f"Error while trying to match hazard time horizon datasets. More info: {exception}",
            )
            return ""

    def get_hazard_dataset_properties(
        self, hazard_type: str, scenario: str, time_horizon: str, country: str
    ) -> dict:
        """
        Get the properties of a hazard dataset based on its type, scenario, time horizon,
        and country, to be used as search parameters in the CLIMADA API Client

        This method retrieves the properties of a hazard dataset based on its type, scenario,
        time horizon, and country. It determines the appropriate properties based on the provided
        parameters and returns them as a dictionary, to be used as search parameters in the
        CLIMADA API Client.

        :param hazard_type: The type of hazard for which to retrieve the dataset properties.
        :type hazard_type: str
        :param scenario: The scenario type, either "historical" or "future".
        :type scenario: str
        :param time_horizon: The time horizon for future scenarios.
        :type time_horizon: str
        :param country: The name of the country for which to retrieve the dataset properties.
        :type country: str
        :return: A dictionary containing the properties of the hazard dataset.
        :rtype: dict
        """
        hazard_properties = {}
        time_horizon = self.get_hazard_time_horizon(hazard_type, scenario, time_horizon)
        if hazard_type == "river_flood":
            hazard_properties = {
                "country_name": country,
                "climate_scenario": scenario,
                "year_range": time_horizon,
            }
        if hazard_type == "tropical_cyclone":
            hazard_properties = {
                "country_name": country,
                "climate_scenario": scenario if scenario != "historical" else None,
                "ref_year": time_horizon,
            }
        if hazard_type == "wildfire":
            hazard_properties = {
                "country_name": country,
                "climate_scenario": "histocial",
                "year_range": time_horizon,
            }
        if hazard_type == "earthquake":
            hazard_properties = {
                "country_name": country,
            }
        if hazard_type == "flood":
            hazard_properties = {
                "country_name": country,
                "year_range": time_horizon,
            }

        return hazard_properties

    def get_hazard(
        self,
        hazard_type: str,
        source: str = None,
        scenario: str = None,
        time_horizon: str = None,
        country: str = None,
        filepath: Path = None,
    ) -> Hazard:
        """
        Retrieve a Hazard object.

        This method retrieves a Hazard object based on the specified parameters, including the
        hazard type, source, scenario, time horizon, country, and filepath. It returns a Hazard
        object representing the retrieved dataset. Hazard objects can be obtained from external
        .mat, .hdf5 or raster files, or from the CLIMADA API Client.

        :param hazard_type: The type of hazard dataset to retrieve.
        :type hazard_type: str
        :param source: The source of the hazard dataset
            (e.g., "mat", "hdf5", "climada_api", "raster").
        :type source: str, optional
        :param scenario: The scenario type for future projections.
        :type scenario: str, optional
        :param time_horizon: The time horizon for future scenarios.
        :type time_horizon: str, optional
        :param country: The name of the country associated with the hazard dataset.
        :type country: str, optional
        :param filepath: The filepath to the hazard dataset file.
        :type filepath: Path, optional
        :return: A Hazard object representing the retrieved hazard dataset.
        :rtype: Hazard
        :raises ValueError: If the specified source is invalid.
        """
        if source and source not in ["mat", "hdf5", "climada_api", "raster"]:
            status_message = (
                "Error while trying to create hazard object. "
                "Source must be chosen from ['mat', 'hdf5', 'climada_api', 'raster']"
            )
            logger.log("error", status_message)
            raise ValueError(status_message)
        if not source:
            if hazard_type == "drought":
                source = "mat"
            if hazard_type == "flood":
                source = "raster"
            if hazard_type == "heatwaves":
                source = "raster"
        if source == "climada_api":
            hazard = self._get_hazard_from_client(hazard_type, scenario, time_horizon, country)
        if source == "raster":
            hazard = self._get_hazard_from_raster(filepath, hazard_type)
        if source == "mat":
            hazard = self._get_hazard_from_mat(filepath)
        if source == "hdf5":
            hazard = self._get_hazard_from_hdf5(filepath)

        return hazard

    def _get_hazard_from_client(
        self, hazard_type: str, scenario: str, time_horizon: str, country: str
    ):
        """
        Retrieve a hazard dataset from the Climada API.

        This method retrieves a hazard dataset from the Climada API based on the specified hazard
        type, scenario, time horizon, and country. It returns a Hazard object representing the
        retrieved dataset.

        :param hazard_type: The type of hazard dataset to retrieve.
        :type hazard_type: str
        :param scenario: The scenario type for future projections.
        :type scenario: str
        :param time_horizon: The time horizon for future scenarios.
        :type time_horizon: str
        :param country: The name of the country associated with the hazard dataset.
        :type country: str
        :return: A Hazard object representing the retrieved hazard dataset.
        :rtype: Hazard
        :raises ValueError: If an error occurs while retrieving the hazard dataset.
        """
        hazard_properties = self.get_hazard_dataset_properties(
            hazard_type, scenario, time_horizon, country
        )
        try:
            hazard = self.client.get_hazard(
                hazard_type=hazard_type,
                properties=hazard_properties,
                dump_dir=DATA_HAZARDS_DIR,
            )
            hazard.intensity_thres = self.get_hazard_intensity_thres(hazard)
            status_message = "Finished fetching hazards from client"
            logger.log("info", status_message)
            return hazard

        except Exception as exc:
            status_message = f"Error while trying to create hazard object. More info: {exc}"
            logger.log("error", status_message)
            raise ValueError(status_message) from exc

    def _get_hazard_from_raster(self, filepath: Path, hazard_type: str) -> Hazard:
        try:
            hazard_code = self.get_hazard_code(hazard_type)
            hazard = Hazard.from_raster(
                DATA_HAZARDS_DIR / filepath,
                attrs={
                    "frequency": np.array([0.5, 0.2, 0.1, 0.04]),
                    "event_id": np.array([1, 2, 3, 4]),
                    "units": "m",
                },
                haz_type=hazard_code,
                band=[1, 2, 3, 4],
            )
            # TODO: Set intensity threshold. This step is required to generate meaningful maps
            # as CLIMADA sets intensity_thres = 10 and in certain hazards this excludes all values.
            intensity_thres = self.get_hazard_intensity_thres(hazard_type)
            hazard.intensity_thres = intensity_thres

            # Set the hazard code
            hazard.haz_type = hazard_code
            # Set hazard units.
            if hazard_code == "FL":
                hazard.units = "m"
            elif hazard_code == "HW":
                hazard.units = ""
            else:
                hazard.units = "m"

            # This step is required to generate the lat/long columns and avoid issues
            # with array size mismatch
            hazard.centroids.set_geometry_points()
            hazard.check()

            return hazard
        except Exception as exception:
            logger.log(
                "error",
                "An unexpected error occurred while trying to create hazard object from mat file."
                f"More info: {exception}",
            )
            return None

    def _get_hazard_from_mat(self, filepath: Path) -> Hazard:
        """
        Retrieve a hazard dataset from a MATLAB file.

        This method retrieves a hazard dataset from a MATLAB file located at the specified
        filepath. It returns a Hazard object representing the retrieved dataset.

        :param filepath: The filepath to the MATLAB file containing the hazard dataset.
        :type filepath: Path
        :return: A Hazard object representing the retrieved hazard dataset.
        :rtype: Hazard
        :raises ValueError: If an error occurs while retrieving the hazard dataset.
        """
        # TODO: Continue implementation
        try:
            hazard = Hazard().from_mat(DATA_HAZARDS_DIR / filepath)
            hazard_type = hazard.haz_type
            # Set intensity threshold according to hazard type
            intensity_thres = self.get_hazard_intensity_thres(hazard_type)
            hazard.intensity_thres = intensity_thres
            # Set hazard intensity unit in case it's not available in the matlab file
            # TODO: In drought we have no units. Change IT to be dynamic according to hazard_type.
            hazard.units = ""

            return hazard
        except Exception as exception:
            logger.log(
                "error",
                "An unexpected error occurred while trying to create hazard object from mat file."
                f"More info: {exception}",
            )
            return None

    # TODO: Extract this to settings file
    def get_hazard_intensity_thres(self, hazard_type: str) -> float:
        """
        Get the intensity threshold for a given hazard type.

        This method returns the intensity threshold corresponding to the specified hazard type.

        :param hazard_type: The type of hazard for which to retrieve the intensity threshold.
        :type hazard_type: str
        :return: The intensity threshold for the specified hazard type.
        :rtype: float
        """
        intensity_thres = -100
        if hazard_type == "RF":
            intensity_thres = 1
        elif hazard_type == "FL":
            intensity_thres = 1
        if hazard_type == "D":
            intensity_thres = -4  # TODO: Test if this is correct
        return intensity_thres

    def get_circle_radius(self, hazard_type: str) -> int:
        """
        Return the radius of a circle based on the hazard type.

        This method returns the radius of a circle based on the specified hazard type.

        :param hazard_type: The type of hazard.
        :type hazard_type: str
        :return: The radius of the circle.
        :rtype: int
        """
        radius = 2000
        if hazard_type == "D":
            radius = 11000
        if hazard_type == "FL":
            radius = 2000
        return radius

    def generate_hazard_geojson(
        self,
        hazard: Hazard,
        country_name: str,
        return_periods: tuple = (25, 20, 15, 10),
    ):
        """
        Generate GeoJSON data for hazard points.

        This method generates GeoJSON data for hazard points based on the specified hazard,
        country name, and return periods.

        :param hazard: The hazard object.
        :type hazard: Hazard
        :param country_name: The name of the country.
        :type country_name: str
        :param return_periods: Tuple of return periods, defaults to (25, 20, 15, 10).
        :type return_periods: tuple, optional
        """
        try:
            country_iso3 = self.base_handler.get_iso3_country_code(country_name)
            admin_gdf = self.base_handler.get_admin_data(country_iso3, 2)
            coords = np.array(hazard.centroids.coord)
            local_exceedance_inten = hazard.local_exceedance_inten(return_periods)
            local_exceedance_inten = pd.DataFrame(local_exceedance_inten).T
            data = np.column_stack((coords, local_exceedance_inten))
            columns = ["latitude", "longitude"] + [f"rp{rp}" for rp in return_periods]

            hazard_df = pd.DataFrame(data, columns=columns)

            # Round the hazard rp values to 2 decimal places. Update is vectorized and efficient
            # for large datasets
            hazard_df.update(hazard_df[[f"rp{rp}" for rp in return_periods]].round(2))
            geometry = [Point(xy) for xy in zip(hazard_df["longitude"], hazard_df["latitude"])]
            hazard_gdf = gpd.GeoDataFrame(hazard_df, geometry=geometry, crs="EPSG:4326")

            # TODO: Test efficiency and remove redundant code. Timings look similar
            # hazard_gdf = gpd.GeoDataFrame(
            #     pd.DataFrame(data, columns=columns),
            #     geometry=gpd.points_from_xy(data[:, 1], data[:, 0], crs="EPSG:4326"),
            # )

            # hazard_gdf.set_crs("EPSG:4326", inplace=True)
            # Filter hazard_gdf to exclude rows where all return period values are zero
            hazard_gdf = hazard_gdf[
                (hazard_gdf[[f"rp{rp}" for rp in return_periods]] != 0).any(axis=1)
            ]

            # Spatial join with administrative areas
            joined_gdf = gpd.sjoin(hazard_gdf, admin_gdf, how="left", predicate="within")
            # Remove points outside of the country
            # TODO: Test if this needs to be refined
            # TODO: Comment out temporarily to resolve empty df issues
            joined_gdf = joined_gdf[~joined_gdf["country"].isna()]
            joined_gdf = joined_gdf.drop(columns=["latitude", "longitude", "index_right"])
            joined_gdf = joined_gdf.reset_index(drop=True)

            radius = self.get_circle_radius(hazard.haz_type)

            # Convert to GeoJSON for this layer and add to all_layers_geojson
            hazard_geojson = joined_gdf.__geo_interface__
            hazard_geojson["_metadata"] = {
                "unit": hazard.units,
                "title": f"Hazard ({hazard.units})" if hazard.units else "Hazard",
                "radius": radius,
            }

            # Save the combined GeoJSON file
            map_data_filepath = DATA_TEMP_DIR / "hazards_geodata.json"
            with open(map_data_filepath, "w", encoding="utf-8") as f:
                json.dump(hazard_geojson, f)
        except Exception as exception:
            logger.log("error", f"An unexpected error occurred. More info: {exception}")

    def _get_hazard_from_hdf5(self, filepath: Path) -> Hazard:
        """
        Read the selected .hdf5 input file and build the necessary hazard data to
        create a Hazard object.

        Parameters
        ----------
        filepath : str, required
            File path of the .hdf5 input file. The file must be placed in the data/hazards folder.

        Returns
        -------
        hazard : climada.hazard.Hazard
            The combined hazard object if the file exists. None if the file does not exist.
        """
        try:
            filepath = DATA_HAZARDS_DIR / filepath
            if filepath.exists():
                logger.log(
                    "info",
                    f"File {filepath} already exists and will be used to create Hazard object.",
                )
                hazard = Hazard.from_hdf5(filepath)
                return hazard
            raise FileExistsError("Hazard file not found")
        except FileExistsError as e:
            logger.log("error", f"File not found: {e}")
            return None
        except Exception as e:
            logger.log("error", f"An unexpected error occurred. More info: {e}")
            return None

    def _get_hazard_from_hdf5(self, filepath: Path) -> Hazard:
        """
        Read the selected .hdf5 input file and build the necessary hazard data to
        create a Hazard object.

        :param filepath: File path of the .hdf5 input file. The file must be placed in
        the data/hazards folder.
        :type filepath: Path
        :return: The combined hazard object if the file exists. None if the file does not exist.
        :rtype: climada.hazard.Hazard
        """
        try:
            hazard_filepath = DATA_HAZARDS_DIR / filepath
            hazard = Hazard().from_excel(hazard_filepath)
            return hazard
        except Exception as exception:
            logger.log(
                "error",
                "An unexpected error occurred while trying to create hazard object from xlsx file."
                f"More info: {exception}",
            )
            return None

    def get_hazard_code(self, hazard_type: str) -> str:
        """
        Retrieve the code corresponding to a given hazard type.

        This function maps a hazard type to its corresponding hazard code. If the hazard type
        is not recognized, it raises a ValueError.

        :param hazard_type: The type of hazard as a string.
        :type hazard_type: str
        :return: The hazard code corresponding to the provided hazard type.
        :rtype: str
        :raises ValueError: If the hazard type is not recognized.
        """
        # Map hazard types to their corresponding codes
        hazard_codes = {
            "tropical_cyclone": "TC",
            "river_flood": "RF",
            "storm_europe": "WS",
            "wildfire": "BF",
            "earthquake": "EQ",
            "flood": "FL",
            "flash_flood": "FL",
            "drought": "D",
            "heatwaves": "HW",
        }

        # Retrieve the code for the given hazard type
        code = hazard_codes.get(hazard_type, None)

        # Raise an exception if the hazard type is not found
        if code is None:
            # raise ValueError(f"Hazard type '{hazard_type}' is not recognized.")
            logger.log(
                "error",
                f"Hazard type '{hazard_type}' is not recognized.",
            )

        return code

    def get_hazard_type(self, hazard_code: str) -> str:
        """
        Retrieve the hazard type corresponding to a given hazard code.

        This function maps a hazard code to its corresponding hazard type. If the hazard code
        is not recognized, it raises a ValueError.

        :param hazard_code: The hazard code as a string.
        :type hazard_code: str
        :return: The hazard type corresponding to the provided hazard code.
        :rtype: str
        :raises ValueError: If the hazard code is not recognized.
        """
        # Reverse mapping of hazard codes to hazard types
        hazard_types = {
            "TC": "tropical_cyclone",
            "RF": "river_flood",
            "WS": "storm_europe",
            "BF": "wildfire",
            "EQ": "earthquake",
            "FL": "flood",
            "D": "drought",
            "HW": "heatwaves",
        }

        # Retrieve the hazard type for the given hazard code
        hazard_type = hazard_types.get(hazard_code, None)

        # Raise an exception if the hazard code is not found
        if hazard_type is None:
            # raise ValueError(f"Hazard code '{hazard_code}' is not recognized.")
            logger.log(
                "error",
                f"Hazard code '{hazard_code}' is not recognized.",
            )

        return hazard_type

    def get_hazard_filename(self, hazard_code: str, country_code: str, scenario: str) -> str:
        """
        Get the hazard filename based on the request parameters.
        This helper method sets the hazard filename in a specific format to be searched
        in the data/hazards directory

        :param is_historical: Flag indicating whether historical hazard should be retrieved.
        :type is_historical: bool
        :return: The hazard filename.
        :rtype: str
        """
        if hazard_code == "D":
            hazard_filename = f"hazard_{hazard_code}_{country_code}_{scenario}.mat"
        elif hazard_code == "FL":
            hazard_filename = f"hazard_{hazard_code}_{country_code}_{scenario}.tif"
        elif hazard_code == "HW":
            hazard_filename = f"hazard_{hazard_code}_{country_code}_{scenario}.tif"
        return hazard_filename
