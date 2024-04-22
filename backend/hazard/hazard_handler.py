import json
from pathlib import Path
from time import time

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

from climada.hazard import Hazard
from climada.util.api_client import Client
from constants import (
    DATA_HAZARDS_DIR,
    DATA_TEMP_DIR,
    REQUIREMENTS_DIR,
)
from handlers import get_iso3_country_code
from logger_config import LoggerConfig

logger = LoggerConfig(logger_types=["file"])


class HazardHandler:
    def __init__(self):
        self.client = Client()

    # TODO: Needs to be refactored
    def get_hazard_time_horizon(self, hazard_type: str, scenario: str, time_horizon: str) -> str:
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

            if scenario == "historical":
                return historical_time_horizons.get(hazard_type, "")
            else:
                if hazard_type == "river_flood":
                    return time_horizon
                elif hazard_type == "tropical_cyclone":
                    return tropical_cyclone_future_mapping.get(time_horizon, "")

            return ""  # Default return if no match found
        except Exception as exception:
            logger.log(
                "error",
                f"Error while trying to match hazard time horizon datasets. More info: {exception}",
            )
            return ""

    def get_hazard_dataset_properties(
        self, hazard_type: str, scenario: str, time_horizon: str, country: str
    ) -> dict:
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

    def get_hazard_unit(self, hazard_type):
        unit = "No unit"
        if hazard_type == "drought":
            pass

    def get_hazard(
        self,
        hazard_code: str,
        source: str = None,
        scenario: str = None,
        time_horizon: str = None,
        country: str = None,
        filepath: Path = None,
    ) -> Hazard:
        """
        Get hazard
        """
        if source and source not in ["mat", "hdf5", "climada_api", "raster"]:
            status_message = f"Error while trying to create hazard object. Source must be chosen from ['mat', 'hdf5', 'climada_api', 'raster']"
            logger.log("error", status_message)
            raise ValueError(status_message)
        if not source:
            if hazard_code == "D":
                source = "mat"
            if hazard_type == "flood":
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
            status_message = f"Finished fetching hazards from client"
            logger.log("info", status_message)
            return hazard

        except Exception as exc:
            status_message = f"Error while trying to create hazard object. More info: {exc}"
            logger.log("error", status_message)
            raise ValueError(status_message)

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
            intensity_thres = self.get_hazard_intensity_thres(hazard_type)
            hazard.intensity_thres = intensity_thres
            hazard.check()

            return hazard
        except Exception as exception:
            logger.log(
                "error",
                f"An unexpected error occurred while trying to create hazard object from mat file. More info: {exception}",
            )
            return None

    def _get_hazard_from_mat(self, filepath: Path) -> Hazard:
        # TODO: Continue implementation
        try:
            hazard = Hazard().from_mat(DATA_HAZARDS_DIR / filepath)
            hazard_type = hazard.haz_type
            # Set intensity threshold according to hazard type
            intensity_thres = self.get_hazard_intensity_thres(hazard_type)
            hazard.intensity_thres = intensity_thres
            # Set hazard intensity unit in case it's not available in the matlab file
            # hazard.units

            return hazard
        except Exception as exception:
            logger.log(
                "error",
                f"An unexpected error occurred while trying to create hazard object from mat file. More info: {exception}",
            )
            return None

    # TODO: Extract this to settings file
    def get_hazard_intensity_thres(self, hazard_type: str) -> float:
        intensity_thres = -100
        if hazard_type == "RF":
            intensity_thres = 1
        elif hazard_type == "FL":
            intensity_thres = 1
        if hazard_type == "D":
            intensity_thres = -4
        return intensity_thres

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

    def get_circle_radius(self, hazard_type: str) -> int:
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
        try:
            country_iso3 = get_iso3_country_code(country_name)
            admin_gdf = self.get_admin_data(country_iso3, 2)
            coords = np.array(hazard.centroids.coord)
            local_exceedance_inten = hazard.local_exceedance_inten(return_periods)
            local_exceedance_inten = pd.DataFrame(local_exceedance_inten).T
            data = np.column_stack((coords, local_exceedance_inten))
            columns = ["latitude", "longitude"] + [f"rp{rp}" for rp in return_periods]

            hazard_df = pd.DataFrame(data, columns=columns)
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
            joined_gdf = joined_gdf[~joined_gdf["country"].isna()]
            joined_gdf = joined_gdf.drop(columns=["latitude", "longitude", "index_right"])
            joined_gdf = joined_gdf.reset_index(drop=True)

            radius = self.get_circle_radius(hazard.haz_type)

            # Convert to GeoJSON for this layer and add to all_layers_geojson
            hazard_geojson = joined_gdf.__geo_interface__
            hazard_geojson["_metadata"] = {
                "unit": hazard.units,
                "title": f"Hazard ({hazard.units})",
                "radius": radius,
            }

            # Save the combined GeoJSON file
            map_data_filepath = DATA_TEMP_DIR / f"hazards_geodata.json"
            with open(map_data_filepath, "w") as f:
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
            else:
                raise FileExistsError("Hazard file not found")
        except FileExistsError as e:
            logger.log("error", f"File not found: {e}")
            return None
        except Exception as e:
            logger.log("error", f"An unexpected error occurred. More info: {e}")
            return None

    def get_hazard_from_xlsx(self, filepath: Path) -> Hazard:
        try:
            hazard_filepath = DATA_HAZARDS_DIR / filepath
            hazard = Hazard().from_excel(hazard_filepath)
            return hazard
        except Exception as exception:
            logger.log(
                "error",
                f"An unexpected error occurred while trying to create hazard object from xlsx file. More info: {exception}",
            )
            return None

    def get_hazard_code(self, hazard_type: str) -> str:
        """
        Retrieve the code corresponding to a given hazard type.

        This function maps a hazard type to its corresponding hazard code. If the hazard type is not recognized, it raises a ValueError.

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

        This function maps a hazard code to its corresponding hazard type. If the hazard code is not recognized, it raises a ValueError.

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
