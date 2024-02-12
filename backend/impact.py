import json

import geopandas as gpd
import numpy as np
import pandas as pd

from climada.engine import Impact, ImpactCalc
from climada.entity import Exposures
from climada.entity.impact_funcs import ImpactFunc, ImpactFuncSet
from climada.entity.impact_funcs.trop_cyclone import ImpfSetTropCyclone
from climada.hazard import Hazard
from constants import (
    DATA_TEMP_DIR,
    REQUIREMENTS_DIR,
)
from handlers import get_iso3_country_code
from logger_config import LoggerConfig

logger = LoggerConfig(logger_types=["file"])


def calculate_impact_function_set(hazard: Hazard) -> ImpactFuncSet:
    impact_function = ImpactFunc()
    impact_function.haz_type = hazard.haz_type
    impact_function.intensity_unit = hazard.units
    impact_function.name = ("Flood Africa JRC Residential",)  # TODO: Needs change

    if hazard.haz_type == "TC":
        impact_function.id = 1
        impact_function_set = ImpfSetTropCyclone.from_calibrated_regional_ImpfSet()
    elif hazard.haz_type == "RF":
        impact_function.id = 3
        impact_function.intensity = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 12.0])
        impact_function.mdd = np.array(
            [0.000, 0.3266, 0.4941, 0.6166, 0.7207, 0.8695, 0.9315, 0.9836, 1.0000, 1.0000]
        )
        impact_function.paa = np.ones(len(impact_function.intensity))
    elif hazard.haz_type == "BF":  # Wildfire
        impact_function.id = 4
        # TODO: Needs to be calidated
        impact_function.intensity = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 12.0])
        impact_function.mdd = np.array(
            [0.000, 0.3266, 0.4941, 0.6166, 0.7207, 0.8695, 0.9315, 0.9836, 1.0000, 1.0000]
        )
        impact_function.paa = np.ones(len(impact_function.intensity))
    elif hazard.haz_type == "FL":  # Flood
        impact_function.id = 5
        # TODO: Needs to be calidated
        impact_function.intensity = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 12.0])
        impact_function.mdd = np.array(
            [0.000, 0.3266, 0.4941, 0.6166, 0.7207, 0.8695, 0.9315, 0.9836, 1.0000, 1.0000]
        )
        impact_function.paa = np.ones(len(impact_function.intensity))
    elif hazard.haz_type == "EQ":  # Earthquake
        impact_function.id = 6
        # TODO: Needs to be calidated
        impact_function.intensity = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 12.0])
        impact_function.mdd = np.array(
            [0.000, 0.3266, 0.4941, 0.6166, 0.7207, 0.8695, 0.9315, 0.9836, 1.0000, 1.0000]
        )
        impact_function.paa = np.ones(len(impact_function.intensity))
    else:  # TODO: Test if we need a default one or filter others out
        impact_function.id = 6
        # TODO: Needs to be calidated
        impact_function.intensity = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 12.0])
        impact_function.mdd = np.array(
            [0.000, 0.3266, 0.4941, 0.6166, 0.7207, 0.8695, 0.9315, 0.9836, 1.0000, 1.0000]
        )
        impact_function.paa = np.ones(len(impact_function.intensity))

    impact_function_set = ImpactFuncSet([impact_function])
    return impact_function_set


def get_impf_id(hazard_type: str) -> int:
    impf_ids = {"TC": 1, "RF": 3, "BF": 4, "FL": 5, "EQ": 6, "DEFAULT": 9}
    return impf_ids.get(hazard_type, impf_ids["DEFAULT"])


def calculate_impact(
    exposure: Exposures, hazard: Hazard, impact_function_set: ImpactFuncSet
) -> Impact:
    try:
        # Assign a default impact function ID to the exposure data
        impf_id = get_impf_id(hazard.haz_type)
        exposure.gdf[f"impf_{hazard.haz_type}"] = impf_id

        # Prepare the impact calculator with the given parameters
        impact_calc = ImpactCalc(
            exposures=exposure,
            impfset=impact_function_set,
            hazard=hazard,
        )
        # Calculate the impact
        impact = impact_calc.impact()
        return impact
    except Exception as exception:
        status_message = f"An error occurred during impact calculation: More info: {exception}"
        logger.log("error", status_message)
        return None


def generate_impact_geojson(
    impact: Impact, country_name: str, return_periods: tuple = (250, 100, 50, 10)
):
    try:
        country_iso3 = get_iso3_country_code(country_name)
        GADM41_filename = REQUIREMENTS_DIR / f"gadm41_{country_iso3}.gpkg"

        admin_gdf = gpd.read_file(filename=GADM41_filename, layer=2)
        coords = np.array(impact.coord_exp)
        local_exceedance_imp = impact.local_exceedance_imp(return_periods)
        local_exceedance_imp = pd.DataFrame(local_exceedance_imp).T
        data = np.column_stack((coords, local_exceedance_imp))
        columns = ["longitude", "latitude"] + [f"rp{rp}" for rp in return_periods]
        impact_gdf = gpd.GeoDataFrame(
            pd.DataFrame(data, columns=columns),
            geometry=gpd.points_from_xy(data[:, 0], data[:, 1]),
        )
        impact_gdf.set_crs("EPSG:4326", inplace=True)

        # Filter hazard_gdf to exclude rows where all return period values are zero
        impact_gdf = impact_gdf[(impact_gdf[[f"rp{rp}" for rp in return_periods]] != 0).any(axis=1)]
        impact_gdf = impact_gdf.drop(columns=["latitude", "longitude"])
        impact_gdf = impact_gdf.reset_index(drop=True)

        # Spatial join with administrative areas
        joined_gdf = gpd.sjoin(impact_gdf, admin_gdf, how="left", predicate="within")
        # Convert to GeoJSON for this layer and add to all_layers_geojson
        impact_geojson = joined_gdf.__geo_interface__

        # Save the combined GeoJSON file
        map_data_filepath = DATA_TEMP_DIR / f"risks_geodata.json"
        with open(map_data_filepath, "w") as f:
            json.dump(impact_geojson, f)
    except Exception as exception:
        logger.log("error", f"An unexpected error occurred. More info: {exception}")
