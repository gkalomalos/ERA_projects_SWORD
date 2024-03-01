from copy import deepcopy
import json
from time import time

import geopandas as gpd

from climada.entity import DiscRates, Entity, Exposures
from climada.entity.measures import MeasureSet
from climada.entity.impact_funcs import ImpactFuncSet
from climada.util.api_client import Client


from constants import DATA_ENTITIES_DIR, DATA_EXPOSURES_DIR, DATA_TEMP_DIR, REQUIREMENTS_DIR
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

    def generate_exposure_geojson(self, exposure: Exposures, country_name: str):
        try:
            exposure_gdf = exposure.gdf
            country_iso3 = get_iso3_country_code(country_name)

            GADM41_filename = REQUIREMENTS_DIR / f"gadm41_{country_iso3}.gpkg"
            layers = [0, 1, 2]

            all_layers_geojson = {"type": "FeatureCollection", "features": []}

            for layer in layers:
                try:
                    admin_gdf = gpd.read_file(filename=GADM41_filename, layer=layer)
                    joined_gdf = gpd.sjoin(exposure_gdf, admin_gdf, how="left", predicate="within")
                    aggregated_values = (
                        joined_gdf.groupby(f"GID_{layer}")["value"].sum().reset_index()
                    )
                    admin_gdf = admin_gdf.merge(aggregated_values, on=f"GID_{layer}", how="left")
                    admin_gdf["value"] = admin_gdf["value"].fillna(0)
                    if layer == 0:
                        admin_gdf_filtered = admin_gdf[["COUNTRY", "geometry", "value"]]
                    elif layer == 1:
                        admin_gdf_filtered = admin_gdf[["COUNTRY", f"NAME_1", "geometry", "value"]]
                    elif layer == 2:
                        admin_gdf_filtered = admin_gdf[
                            ["COUNTRY", f"NAME_1", "NAME_2", "geometry", "value"]
                        ]
                    else:
                        admin_gdf_filtered = admin_gdf[["COUNTRY", "geometry", "value"]]

                    # Convert each layer to a GeoJSON Feature and add it to the collection
                    layer_features = admin_gdf_filtered.__geo_interface__["features"]
                    for feature in layer_features:
                        feature["properties"]["layer"] = layer
                        all_layers_geojson["features"].append(feature)

                except FileNotFoundError:
                    logger.log("error", f"File not found: {GADM41_filename}")
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

    def get_entity(
        self,
        exposure: Exposures,
        discount_rates: DiscRates,
        impact_function_set: ImpactFuncSet,
        measure_set: MeasureSet,
    ) -> Entity:
        """
        Initializes and returns an Entity object based on the provided exposure data,
        discount rates, impact function set, and adaptation measure set.

        :param exposure: The exposure data for the entity.
        :type exposure: Exposure
        :param discount_rates: A list of discount rates applicable to the entity.
        :type discount_rates: list
        :param impact_function_set: The set of impact functions associated with the entity.
        :type impact_function_set: ImpactFunctionSet
        :param measure_set: The set of adaptation measures applicable to the entity.
        :type measure_set: MeasureSet
        :return: An initialized Entity object.
        :rtype: Entity

        :raises ValueError: If any of the inputs are not valid or are missing necessary data.
        """
        try:
            if not exposure or not discount_rates or not impact_function_set or not measure_set:
                raise ValueError("All parameters must be provided and valid.")

            entity = Entity(exposure, discount_rates, impact_function_set, measure_set)
            return entity
        except Exception as e:
            logger.log("error", f"Failed to initialize Entity object: {e}")
            raise ValueError(f"Failed to initialize Entity object: {e}")

    def get_entity_from_xlsx(self, filepath: str) -> Entity:
        try:
            entity_filepath = DATA_ENTITIES_DIR / filepath
            entity = Entity.from_excel(entity_filepath)
            entity.check()

            # columns = [
            #     "category_id",
            #     "latitude",
            #     "longitude",
            #     "value",
            #     "value unit",
            #     "deductible",
            #     "cover",
            #     "impact_fun_id",
            #     "region_id",
            # ]

            # exposure = entity.exposures
            # exposure.gdf = exposure.gdf[columns]
            # exposure.check()

            return entity
        except Exception as exc:
            logger.log(
                "error",
                f"An error occurred while trying to create entity from xlsx. More info: {exc}",
            )
            return None
