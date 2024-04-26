"""
Module for handling exposure data and operations.

This module contains the `ExposureHandler` class, which manages exposure-related operations such as
fetching exposure data from an API, calculating exposure growth, retrieving administrative data, 
and generating exposure GeoJSON files.

Classes:

- `ExposureHandler`: 
    Class for handling exposure data and operations.

Methods:

- `get_exposure_from_api`: 
    Retrieve exposure data from an API for a specific country.
- `get_growth_exposure`: 
    Calculate exposure growth based on annual growth rate and future year.
- `get_admin_data`: 
    Retrieve administrative data for a specific country and administrative level.
- `generate_exposure_geojson`: 
    Generate GeoJSON files for exposure data.
"""

from copy import deepcopy
import json
from time import time

import geopandas as gpd

from climada.entity import Exposures
from climada.util.api_client import Client


from constants import DATA_EXPOSURES_DIR, DATA_TEMP_DIR, REQUIREMENTS_DIR
from handlers import get_iso3_country_code
from logger_config import LoggerConfig

logger = LoggerConfig(logger_types=["file"])


class ExposureHandler:
    """
    Class for handling exposure data and operations.

    This class provides methods for fetching exposure data from an API, calculating exposure growth,
    retrieving administrative data, and generating exposure GeoJSON files.
    """

    def __init__(self):
        self.client = Client()

    def get_exposure_from_api(self, country: str) -> Exposures:
        """
        Retrieves exposure data from an API for a specified country.

        Fetches exposure data for the given country from CLIMADA's API. If any errors occur
        during the process, it logs an error message and raises a ValueError with details.

        :param country: The name of the country for which exposure data is requested.
        :type country: str
        :return: An Exposures object containing exposure data for the specified country.
        :rtype: Exposures
        :raises ValueError: If an error occurs during the exposure data retrieval process.
        """
        start_time = time()
        try:
            exposure = self.client.get_litpop(
                country=country, exponents=(1, 1), dump_dir=DATA_EXPOSURES_DIR
            )
            status_message = f"Finished fetching exposure from client in {time() - start_time}sec."
            logger.log("info", status_message)
            return exposure

        except Exception as exc:
            status_message = f"Error while trying to fetch exposure for {country}. More info: {exc}"
            logger.log("error", status_message)
            raise ValueError(status_message)

    def get_growth_exposure(
        self, exposure: Exposures, annual_growth: float, future_year: int
    ) -> Exposures:
        """
        Calculates the growth of exposure data for a future year based on the provided
        annual growth rate.

        This method calculates the exposure growth for a future year based on the provided
        annual growth rate. It takes the current exposure data, the annual growth rate,
        and the future year as input parameters. If successful, it returns an Exposures object
        containing the exposure data for the future year. If any errors occur during the
        calculation process, it logs an error message and returns None.

        :param exposure: The Exposures object containing the current exposure data.
        :type exposure: Exposures
        :param annual_growth: The annual growth rate used to calculate the exposure growth.
        :type annual_growth: float
        :param future_year: The year for which the exposure growth is calculated.
        :type future_year: int
        :return: An Exposures object containing the exposure data for the future year.
        :rtype: Exposures
        """
        try:
            present_year = exposure.ref_year
            exposure_future = deepcopy(exposure)
            exposure_future.ref_year = future_year
            number_of_years = future_year - present_year + 1
            growth = annual_growth**number_of_years
            exposure_future.gdf["value"] = exposure_future.gdf["value"] * growth
            return exposure_future
        except Exception as exc:
            logger.log(
                "error", f"An error occurred while trying to calculate exposure growth rate: {exc}"
            )
            return None

    def get_admin_data(self, country_code: str, admin_level) -> gpd.GeoDataFrame:
        """
        Retrieves administrative data for a specific country and administrative level.

        This method retrieves administrative data for a specific country and administrative level
        from a GeoJSON file. It constructs the file path based on the provided country code
        and administrative level, reads the GeoJSON file, and returns a GeoDataFrame containing
        the administrative data. If the file is not found or any errors occur during the process,
        it logs an error message and returns None.

        :param country_code: The country code representing the specific country.
        :type country_code: str
        :param admin_level: The administrative level for which data is retrieved.
        :type admin_level: int
        :return: A GeoDataFrame containing the administrative data for the specified country
                and level, or None if the file is not found or errors occur.
        :rtype: gpd.GeoDataFrame
        """
        try:
            file_path = REQUIREMENTS_DIR / f"gadm{admin_level}_{country_code}.geojson"
            admin_gdf = gpd.read_file(file_path)
            admin_gdf = admin_gdf[["shapeName", "shapeID", "shapeGroup", "geometry"]]
            admin_gdf = admin_gdf.rename(
                columns={
                    "shapeID": "id",
                    "shapeName": f"name",
                    "shapeGroup": "country",
                }
            )
            return admin_gdf
        except FileNotFoundError:
            logger.log("error", f"File not found: {file_path}")
        except Exception as exception:
            logger.log(
                "error",
                f"An error occured while trying to get country admin level information."
                f" More info: {exception}",
            )

    def generate_exposure_geojson(self, exposure: Exposures, country_name: str):
        """
        Generate GeoJSON files for exposure data.

        This method generates GeoJSON files for exposure data based on the provided Exposures
        object and country name. It constructs GeoDataFrames from the exposure data, aggregates
        values based on administrative layers, and converts the data to GeoJSON format.
        The generated GeoJSON files include metadata such as unit and title. If any errors occur
        during the process, it logs an error message.

        :param exposure: The Exposures object containing the exposure data.
        :type exposure: Exposures
        :param country_name: The name of the country for which exposure data is generated.
        :type country_name: str
        """
        try:
            exp_gdf = exposure.gdf
            # Cast DataFrame to GeoDataFrame to avoid issues with gpd.sjoin later
            exposure_gdf = gpd.GeoDataFrame(
                exp_gdf,
                geometry=gpd.points_from_xy(
                    exp_gdf["longitude"], exp_gdf["latitude"], crs="EPSG:4326"
                ),
            )
            country_iso3 = get_iso3_country_code(country_name)
            layers = [0, 1, 2]
            all_layers_geojson = {"type": "FeatureCollection", "features": []}

            for layer in layers:
                try:
                    admin_gdf = self.get_admin_data(country_iso3, layer)
                    joined_gdf = gpd.sjoin(exposure_gdf, admin_gdf, how="left", predicate="within")
                    aggregated_values = joined_gdf.groupby(f"id")["value"].sum().reset_index()
                    admin_gdf = admin_gdf.merge(aggregated_values, on=f"id", how="left")
                    admin_gdf["value"] = admin_gdf["value"].round(2).fillna(0)

                    # Convert each layer to a GeoJSON Feature and add it to the collection
                    layer_features = admin_gdf.__geo_interface__["features"]
                    for feature in layer_features:
                        feature["properties"]["layer"] = layer
                        all_layers_geojson["features"].append(feature)
                    all_layers_geojson["_metadata"] = {
                        "unit": exposure.value_unit,
                        "title": f"Exposure ({exposure.value_unit})",
                    }
                except Exception as e:
                    logger.log("error", f"An error occurred while processing layer {layer}: {e}")

            # Save the combined GeoJSON file
            map_data_filepath = DATA_TEMP_DIR / "exposures_geodata.json"
            with open(map_data_filepath, "w") as f:
                json.dump(all_layers_geojson, f)

        except AttributeError as e:
            logger.log("error", f"Invalid Exposure object: {e}")
        except Exception as e:
            logger.log("error", f"An unexpected error occurred: {e}")
