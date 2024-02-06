from datetime import datetime
import json
from time import time

import geopandas as gpd
import numpy as np
import pandas as pd
import pycountry

from climada.engine import Impact, ImpactCalc
from climada.entity import Entity, Exposures
from climada.entity.impact_funcs import ImpactFunc, ImpactFuncSet
from climada.entity.impact_funcs.trop_cyclone import ImpfSetTropCyclone
from climada.hazard import Hazard
from climada.util.api_client import Client
from scipy.interpolate import interp1d
from constants import DATA_EXPOSURES_DIR, DATA_HAZARDS_DIR, DATA_TEMP_DIR, REQUIREMENTS_DIR
from logger_config import LoggerConfig

logger = LoggerConfig(logger_types=["file"])


# EXPOSURE METHODS DEFINITION


def get_exposure(country: str) -> Exposures:
    start_time = time()
    client = Client()
    try:
        exposure = client.get_litpop(country=country, exponents=(1, 1), dump_dir=DATA_EXPOSURES_DIR)
        status_message = f"Finished fetching exposure from client in {time() - start_time}sec."
        logger.log("info", status_message)
        return exposure

    except Exception as exc:
        status_message = f"Error while trying to fetch exposure for {country}. More info: {exc}"
        logger.log("error", status_message)
        raise ValueError(status_message)


def generate_exposure_geojson(exposure: Exposures, country_name: str):
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
                aggregated_values = joined_gdf.groupby(f"GID_{layer}")["value"].sum().reset_index()
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


def get_entity_from_xlsx(filepath: str) -> Entity:
    try:
        entity_filepath = DATA_EXPOSURES_DIR / filepath
        entity = Entity.from_excel(entity_filepath)
        return entity
    except Exception as exc:
        logger.log("error", f"An error occurred while trying to create entity from xlsx: {exc}")
        return None


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


# HAZARD METHODS DEFINITION


# TODO: Needs to be refactored
def get_hazard_time_horizon(hazard_type: str, scenario: str, time_horizon: str) -> str:
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
    hazard_type: str, scenario: str, time_horizon: str, country: str
) -> dict:
    hazard_properties = {}
    time_horizon = get_hazard_time_horizon(hazard_type, scenario, time_horizon)
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


def get_hazard(hazard_type: str, scenario: str, time_horizon: str, country: str) -> Hazard:
    start_time = time()

    hazard_properties = get_hazard_dataset_properties(hazard_type, scenario, time_horizon, country)
    try:
        client = Client()
        hazard = client.get_hazard(
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
def get_hazard_intensity_thres(hazard: Hazard) -> float:
    hazard_type = hazard.haz_type
    intensity_thres = hazard.intensity_thres
    if hazard_type == "RF":
        intensity_thres = 1
    return intensity_thres


def generate_hazard_geojson(
    hazard: Hazard,
    country_name: str,
    return_periods: tuple = (250, 100, 50, 10),
):
    try:
        country_iso3 = get_iso3_country_code(country_name)
        GADM41_filename = REQUIREMENTS_DIR / f"gadm41_{country_iso3}.gpkg"
        intensity_thres = get_hazard_intensity_thres(hazard)
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
        hazard_gdf = hazard_gdf[(hazard_gdf[[f"rp{rp}" for rp in return_periods]] != 0).any(axis=1)]
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


def get_hazard_from_hdf5(filepath) -> Hazard:
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
                "info", f"File {filepath} already exists and will be used to create Hazard object."
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


def get_hazard_from_xlsx(filepath) -> Hazard:
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


def get_hazard_scenario_from_Hazard(hazard: Hazard) -> list:
    """
    Determine the hazard scenario from the given Hazard object.

    Parameters
    -----------
    hazard : Hazard
        The Hazard object containing the file name information used to identify the scenario.

    Returns
    --------
    str
        The identified hazard scenario as a string, or an empty string if no scenario is found.

    Notes
    ------
    This method attempts to match the scenario of a given Hazard object by analyzing its file name attribute. It
    iterates through a predefined list of possible scenarios and returns the first scenario found in the file names.
    If no matching scenario is found, an empty string is returned.
    """
    # Split the file names by ';' and store them in a list
    file_names = hazard.file_name.split(";")

    # Define the list of possible scenarios
    scenarios = ["rcp26", "rcp60", "rcp85", "hist"]
    scenario = []
    try:
        # Find the first matching scenario in the file names
        sc = next((s for s in scenarios for fn in file_names if s in fn), "")
        if sc == "hist":
            sc = "historical"
        scenario = [sc]
    except Exception as exc:
        status_message = f"Error while trying to match hazard type and scenario. More info: {exc}"
        raise Exception(status_message)

    return scenario


def get_hazard_time_horizon_from_Hazard(hazard: Hazard) -> list:
    """
    Determine the hazard time horizon from the given Hazard object.

    Parameters
    -----------
    hazard : Hazard
        The Hazard object containing event date information used to identify the time horizon.

    Returns
    --------
    list
        A list containing a single string representing the matching time horizon in the format "start_year-end_year".
        If no matching time horizon is found, the list will be empty.

    Notes
    ------
    This method attempts to match the time horizon of a given Hazard object by analyzing its event dates.
    It iterates through a predefined list of possible year ranges and returns the first matching range
    where the minimum and maximum event dates fall within the same range.
    If no matching range is found, an empty list is returned.
    """
    try:
        scenario = get_hazard_scenario_from_Hazard(hazard)
        hazard_type = hazard.haz_type
        if scenario == ["historical"]:
            if hazard_type == "WS":
                return ["1940_2014"]
            if hazard_type == "RF":
                return ["1980_2000"]
            if hazard_type == "TC":
                return ["1980_2000"]
            if hazard_type == "EQ":
                return ["1980_2000"]

        else:
            # Get event dates as a list of strings and convert them to datetime objects
            dates = [
                datetime.strptime(date_string, "%Y-%m-%d")
                for date_string in hazard.get_event_date()
            ]

            # Find the min and max dates
            min_date, max_date = min(dates), max(dates)

            # Define year ranges as a list of tuples
            year_ranges = [
                (2010, 2030),
                (2030, 2050),
                (2050, 2070),
                (2070, 2090),
            ]

            # Find the matching year range
            matching_range = next(
                (start_year, end_year)
                for start_year, end_year in year_ranges
                if start_year <= min_date.year < end_year and start_year <= max_date.year < end_year
            )

            # Return the matching range as a list of formatted strings, or an empty list if no match was found
            return [f"{matching_range[0]}-{matching_range[1]}"] if matching_range else []
    except Exception as e:
        print("e:", e)
        return []


# IMPACT METHODS DEFINITION


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


# GENERIC METHODS DEFINITION


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
    time_horizon_beautified = beautify_time_horizon(time_horizon)

    if scenario == "historical":
        map_title = f"{hazard_beautified} risk analysis for {country_beautified} in {time_horizon_beautified} ({scenario_beautified} scenario)."
    else:
        map_title = f"{hazard_beautified} risk analysis for {country_beautified} in {time_horizon_beautified} (scenario {scenario_beautified})."
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


def beautify_time_horizon(time_horizon: str) -> str:
    """
    Get a beautified version of the time horizon to use in UI and reports.

    Parameters
    ----------
    time_horizon: str, required
        Time horizon to search datasets.
        Example: 1980-2000, 2030-2050 etc.

    Returns
    -------
    time_horizon_beautified: str
        The beautified string version of the time horizon.
    """
    time_horizon_beautified = ""
    if time_horizon == "1940_2014":
        time_horizon_beautified = "2014"
    if time_horizon == "1980_2000":
        time_horizon_beautified = "2000"
    if time_horizon == "2010_2030":
        time_horizon_beautified = "2020"
    if time_horizon == "2030_2050":
        time_horizon_beautified = "2040"
    if time_horizon == "2050_2070":
        time_horizon_beautified = "2060"
    if time_horizon == "2070_2090":
        time_horizon_beautified = "2080"
    if time_horizon == "2040":
        time_horizon_beautified = "2040"
    if time_horizon == "2060":
        time_horizon_beautified = "2060"
    if time_horizon == "2080":
        time_horizon_beautified = "2080"

    return time_horizon_beautified


def clear_temp_dir():
    """
    Clear all helper temp files from the temp directory.
    """
    try:
        for file in DATA_TEMP_DIR.glob("*"):
            file.unlink(missing_ok=True)
    except Exception as exc:
        logger.log("ερρορ", f"Error while trying to clear temp directory. More info: {exc}")
