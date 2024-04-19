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
    def __init__(self):
        self.client = Client()

    def get_exposure(self, country: str) -> Exposures:
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
        Return country GeoDataFrame per admin level
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
                f"An error occured while trying to get country admin level information. More info: {exception}",
            )

    def generate_exposure_geojson(self, exposure: Exposures, country_name: str):
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
