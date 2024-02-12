import json
from pathlib import Path
from time import time

import geopandas as gpd
import numpy as np
import pandas as pd

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

    def get_hazard(
        self, hazard_type: str, scenario: str, time_horizon: str, country: str
    ) -> Hazard:
        start_time = time()

        hazard_properties = self.get_hazard_dataset_properties(
            hazard_type, scenario, time_horizon, country
        )
        try:
            hazard = self.client.get_hazard(
                hazard_type=hazard_type,
                properties=hazard_properties,
                dump_dir=DATA_HAZARDS_DIR,
            )
            status_message = f"Finished fetching hazards from client in {time() - start_time}sec."
            logger.log("info", status_message)
            return hazard

        except Exception as exc:
            status_message = f"Error while trying to create hazard object. More info: {exc}"
            logger.log("error", status_message)
            raise ValueError(status_message)

    # TODO: Extract this to settings file
    def get_hazard_intensity_thres(self, hazard: Hazard) -> float:
        hazard_type = hazard.haz_type
        intensity_thres = hazard.intensity_thres
        if hazard_type == "RF":
            intensity_thres = 1
        return intensity_thres

    def generate_hazard_geojson(
        self,
        hazard: Hazard,
        country_name: str,
        return_periods: tuple = (250, 100, 50, 10),
    ):
        try:
            country_iso3 = get_iso3_country_code(country_name)
            GADM41_filename = REQUIREMENTS_DIR / f"gadm41_{country_iso3}.gpkg"
            intensity_thres = self.get_hazard_intensity_thres(hazard)
            hazard.intensity_thres = intensity_thres

            admin_gdf = gpd.read_file(filename=GADM41_filename, layer=2)
            coords = np.array(hazard.centroids.coord)
            local_exceedance_inten = hazard.local_exceedance_inten(return_periods)
            local_exceedance_inten = pd.DataFrame(local_exceedance_inten).T
            data = np.column_stack((coords, local_exceedance_inten))
            columns = ["longitude", "latitude"] + [f"rp{rp}" for rp in return_periods]
            hazard_gdf = gpd.GeoDataFrame(
                pd.DataFrame(data, columns=columns),
                geometry=gpd.points_from_xy(data[:, 0], data[:, 1]),
            )
            hazard_gdf.set_crs("EPSG:4326", inplace=True)
            # Filter hazard_gdf to exclude rows where all return period values are zero
            hazard_gdf = hazard_gdf[
                (hazard_gdf[[f"rp{rp}" for rp in return_periods]] != 0).any(axis=1)
            ]
            hazard_gdf = hazard_gdf.drop(columns=["latitude", "longitude"])
            hazard_gdf = hazard_gdf.reset_index(drop=True)

            # Spatial join with administrative areas
            joined_gdf = gpd.sjoin(hazard_gdf, admin_gdf, how="left", predicate="within")
            # Convert to GeoJSON for this layer and add to all_layers_geojson
            hazard_geojson = joined_gdf.__geo_interface__

            # Save the combined GeoJSON file
            map_data_filepath = DATA_TEMP_DIR / f"hazards_geodata.json"
            with open(map_data_filepath, "w") as f:
                json.dump(hazard_geojson, f)
        except Exception as exception:
            logger.log("error", f"An unexpected error occurred. More info: {exception}")

    def get_hazard_from_hdf5(self, filepath: Path) -> Hazard:
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
            hazard = Hazard()
            hazard.from_excel(hazard_filepath)
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
        # Mapping of hazard types to their corresponding codes
        hazard_codes = {
            "tropical_cyclone": "TC",
            "river_flood": "RF",
            "storm_europe": "WS",
            "wildfire": "BF",
            "earthquake": "EQ",
            "flood": "FL",
        }

        # Attempt to retrieve the code for the given hazard type
        code = hazard_codes.get(hazard_type)

        # Raise an exception if the hazard type is not found
        if code is None:
            raise ValueError(f"Hazard type '{hazard_type}' is not recognized.")

        return code
