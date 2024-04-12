import json

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

from climada.engine import Impact, ImpactCalc
from climada.entity import Exposures
from climada.entity.impact_funcs import ImpactFunc, ImpactFuncSet
from climada.hazard import Hazard
from constants import (
    DATA_TEMP_DIR,
    REQUIREMENTS_DIR,
)
from handlers import get_iso3_country_code
from logger_config import LoggerConfig

logger = LoggerConfig(logger_types=["file"])


class ImpactHandler:
    def get_impact_function_set(self, exposure_type: str, hazard_type: str) -> ImpactFuncSet:
        """Get the impact function based on the given ID."""
        impf = ImpactFunc()
        # Flood impact functions
        if exposure_type == "buddhist_monks" and hazard_type == "flood":
            impf = ImpactFunc(
                haz_type="FL",
                id=101,
                intensity=np.array(
                    [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0, 5.0]
                ),
                mdd=np.array(
                    [
                        0.0,
                        0.0,
                        1.0,
                        1.0,
                        1.0,
                        1.0,
                        1.0,
                        1.0,
                        1.0,
                        1.0,
                        1.0,
                        1.0,
                    ]
                ),
                paa=np.ones(12),
                intensity_unit="People",
                name="Buddhist monks",
            )
        elif exposure_type == "students" and hazard_type == "flood":
            impf = ImpactFunc(
                haz_type="FL",
                id=102,
                intensity=np.array([0.0, 0.3, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0, 5.0]),
                mdd=np.array(
                    [
                        0.0,
                        1.0,
                        1.0,
                        1.0,
                        1.0,
                        1.0,
                        1.0,
                        1.0,
                        1.0,
                        1.0,
                        1.0,
                        1.0,
                    ]
                ),
                paa=np.ones(12),
                intensity_unit="People",
                name="Students",
            )
        elif exposure_type == "tree_crops_farmers" and hazard_type == "flood":
            impf = ImpactFunc(
                haz_type="FL",
                id=103,
                intensity=np.array(
                    [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0, 5.0]
                ),
                mdd=np.array(
                    [
                        0.0,
                        -0.0061,
                        -0.003,
                        0.0082,
                        0.0262,
                        0.0495,
                        0.0765,
                        0.1054,
                        0.1346,
                        0.2246,
                        0.2318,
                        0.2318,
                    ]
                ),
                paa=np.ones(12),
                intensity_unit="People",
                name="Tree crops farmers",
            )
        elif exposure_type == "grass_crops_farmers" and hazard_type == "flood":
            impf = ImpactFunc(
                haz_type="FL",
                id=104,
                intensity=np.array(
                    [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0, 5.0]
                ),
                mdd=np.array(
                    [
                        0.0,
                        0.0,
                        0.0067,
                        0.0454,
                        0.0975,
                        0.1537,
                        0.2074,
                        0.2543,
                        0.2922,
                        0.3203,
                        0.3300,
                        0.3300,
                    ]
                ),
                paa=np.ones(12),
                intensity_unit="People",
                name="Grass crops farmers",
            )
        elif exposure_type == "diarrhoea_patients" and hazard_type == "flood":
            impf = ImpactFunc(
                haz_type="FL",
                id=105,
                intensity=np.array([0.01, 0.08, 0.44, 2]),
                mdd=np.array([0.0001, 0.0002, 0.0004, 0.0009]),
                paa=np.ones(4),
                intensity_unit="People",
                name="Diarrhoea patients",
            )
        elif exposure_type == "tree_crops" and hazard_type == "flood":
            impf = ImpactFunc(
                haz_type="D",
                id=201,
                intensity=np.array(
                    [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0, 5.0]
                ),
                mdd=np.array(
                    [
                        0.0,
                        -0.0061,
                        -0.003,
                        0.0082,
                        0.0262,
                        0.0495,
                        0.0765,
                        0.1054,
                        0.1346,
                        0.2246,
                        0.2318,
                        0.2318,
                    ]
                ),
                paa=np.ones(12),
                intensity_unit="SPI",
                name="Tree crops",
            )
        elif exposure_type == "grass_crops" and hazard_type == "flood":
            impf = ImpactFunc(
                haz_type="D",
                id=202,
                intensity=np.array(
                    [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0, 5.0]
                ),
                mdd=np.array(
                    [
                        0.0,
                        0.0,
                        0.0067,
                        0.0454,
                        0.0975,
                        0.1537,
                        0.2074,
                        0.2543,
                        0.2922,
                        0.3203,
                        0.3300,
                        0.3300,
                    ]
                ),
                paa=np.ones(12),
                intensity_unit="SPI",
                name="Grass crops",
            )
        elif exposure_type == "wet_markets" and hazard_type == "flood":
            impf = ImpactFunc(
                haz_type="D",
                id=203,
                intensity=np.array(
                    [0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 3.0, 4.0, 5.0]
                ),
                mdd=np.array(
                    [
                        0.0,
                        0.0,
                        0.0067,
                        0.0454,
                        0.0975,
                        0.1537,
                        0.2074,
                        0.2543,
                        0.2922,
                        0.3203,
                        0.3300,
                        0.3300,
                    ]
                ),
                paa=np.ones(12),
                intensity_unit="SPI",
                name="Markets",
            )
        elif exposure_type == "roads" and hazard_type == "flood":
            impf = ImpactFunc(
                haz_type="D",
                id=301,
                intensity=np.array([0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]),
                mdd=np.array([0.0, 0.0, 0.0, 1.0, 1.0, 1.0, 1.0]),
                paa=np.ones(7),
                intensity_unit="SPI",
                name="Mobility",
            )

        # Drought impact functions
        elif exposure_type == "tree_crops_farmers" and hazard_type == "drought":
            impf = ImpactFunc(
                haz_type="D",
                id=103,
                intensity=np.array([-3.5, -3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5]),
                mdd=np.array([0.6667, 0.6667, 0.3906, 0.2232, 0.1216, 0.0600, 0.0227, 0.0, 0.0]),
                paa=np.ones(9),
                intensity_unit="SPI",
                name="Tree crop farmers",
            )
        elif exposure_type == "grass_crops_farmers" and hazard_type == "drought":
            impf = ImpactFunc(
                haz_type="D",
                id=104,
                intensity=np.array([-3.5, -3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5]),
                mdd=np.array([1.0, 1.0, 1.0, 0.7365, 0.4013, 0.1981, 0.0748, 0.0, 0.0]),
                paa=np.ones(9),
                intensity_unit="SPI",
                name="Tree crop farmers",
            )
        elif exposure_type == "water_users" and hazard_type == "drought":
            impf = ImpactFunc(
                haz_type="D",
                id=105,
                intensity=np.array([-3.5, -3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5]),
                mdd=np.array([1.0, 0.5871, 0.3362, 0.1925, 0.1102, 0.0631, 0.0361, 0.0207, 0.0119]),
                paa=np.ones(9),
                intensity_unit="SPI",
                name="Unmet water demand",
            )
        elif exposure_type == "tree_crops" and hazard_type == "drought":
            impf = ImpactFunc(
                haz_type="D",
                id=201,
                intensity=np.array([-3.5, -3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5]),
                mdd=np.array([0.4667, 0.1867, 0.0706, 0.0332, 0.0216, 0.0130, 0.0107, 0.0, 0.0]),
                paa=np.ones(9),
                intensity_unit="SPI",
                name="Tree crops",
            )
        elif exposure_type == "grass_crops" and hazard_type == "drought":
            impf = ImpactFunc(
                haz_type="D",
                id=202,
                intensity=np.array([-3.5, -3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5]),
                mdd=np.array([0.60, 0.20, 0.15, 0.10, 0.0713, 0.0381, 0.0148, 0.0, 0.0]),
                paa=np.ones(9),
                intensity_unit="SPI",
                name="Grass crops",
            )
        elif exposure_type == "wet_markets" and hazard_type == "drought":
            impf = ImpactFunc(
                haz_type="D",
                id=203,
                intensity=np.array([-3.5, -3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5]),
                mdd=np.array([0.7, 0.25, 0.18, 0.12, 0.0613, 0.0381, 0.0148, 0, 0]),
                paa=np.ones(9),
                intensity_unit="SPI",
                name="Markets",
            )
        elif id == 401:
            pass
        elif id == 402:
            pass

        impfset = ImpactFuncSet([impf])
        return impfset

    def get_impf_id(self, hazard_type: str) -> int:
        impf_ids = {"TC": 1, "RF": 3, "BF": 4, "FL": 5, "EQ": 6, "DEFAULT": 9}
        return impf_ids.get(hazard_type, impf_ids["DEFAULT"])

    def calculate_impact(
        self, exposure: Exposures, hazard: Hazard, impact_function_set: ImpactFuncSet
    ) -> Impact:
        try:
            # Assign a default impact function ID to the exposure data
            # impf_id = self.get_impf_id(hazard.haz_type)
            # exposure.gdf[f"impf_{hazard.haz_type}"] = impf_id

            # Prepare the impact calculator with the given parameters
            impact_calc = ImpactCalc(
                exposures=exposure,
                impfset=impact_function_set,
                hazard=hazard,
            )
            # Calculate the impact
            impact = impact_calc.impact(save_mat=True, assign_centroids=True)
            return impact
        except Exception as exception:
            status_message = f"An error occurred during impact calculation: More info: {exception}"
            logger.log("error", status_message)
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

    def generate_impact_geojson(
        self, impact: Impact, country_name: str, return_periods: tuple = (25, 20, 15, 10)
    ):
        try:
            country_iso3 = get_iso3_country_code(country_name)
            admin_gdf = self.get_admin_data(country_iso3, 2)
            coords = np.array(impact.coord_exp)
            local_exceedance_imp = impact.local_exceedance_imp(return_periods)
            local_exceedance_imp = pd.DataFrame(local_exceedance_imp).T
            data = np.column_stack((coords, local_exceedance_imp))
            columns = ["latitude", "longitude"] + [f"rp{rp}" for rp in return_periods]

            impact_df = pd.DataFrame(data, columns=columns)
            geometry = [Point(xy) for xy in zip(impact_df["longitude"], impact_df["latitude"])]
            impact_gdf = gpd.GeoDataFrame(impact_df, geometry=geometry, crs="EPSG:4326")

            # TODO: Test efficiency and remove redundant code. Timings look similar
            # impact_gdf = gpd.GeoDataFrame(
            #     pd.DataFrame(data, columns=columns),
            #     geometry=gpd.points_from_xy(data[:, 0], data[:, 1]),
            # )
            # impact_gdf.set_crs("EPSG:4326", inplace=True)

            # Filter hazard_gdf to exclude rows where all return period values are zero
            impact_gdf = impact_gdf[
                (impact_gdf[[f"rp{rp}" for rp in return_periods]] != 0).any(axis=1)
            ]
            impact_gdf = impact_gdf.drop(columns=["latitude", "longitude"])
            impact_gdf = impact_gdf.reset_index(drop=True)

            # Spatial join with administrative areas
            joined_gdf = gpd.sjoin(impact_gdf, admin_gdf, how="left", predicate="within")
            # Convert to GeoJSON for this layer and add to all_layers_geojson
            impact_geojson = joined_gdf.__geo_interface__
            impact_geojson["_metadata"] = {"unit": impact.unit, "title": f"Risk ({impact.unit})"}

            # Save the combined GeoJSON file
            map_data_filepath = DATA_TEMP_DIR / f"risks_geodata.json"
            with open(map_data_filepath, "w") as f:
                json.dump(impact_geojson, f)
        except Exception as exception:
            logger.log("error", f"An unexpected error occurred. More info: {exception}")
