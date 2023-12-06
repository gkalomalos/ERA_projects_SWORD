import json
from copy import deepcopy
from json import loads
from os import path
from pathlib import Path
from re import split
from time import time
from datetime import datetime
import urllib.request

import geopandas as gpd
from geopandas.tools import sjoin
import numpy as np
import pandas as pd
import pycountry

from climada.engine import Impact
from climada.entity import Exposures
from climada.entity.impact_funcs import ImpactFunc, ImpactFuncSet, ImpfTropCyclone
from climada.entity.impact_funcs.storm_europe import ImpfStormEurope
from climada.entity.impact_funcs.trop_cyclone import ImpfSetTropCyclone
from climada.hazard import Hazard
from climada.util.api_client import Client, DatasetInfo, DataTypeShortInfo, FileInfo
from scipy.interpolate import interp1d
from constants import (
    CLIENT_ASSETS_DIR,
    CURRENCY_RATES,
    DATA_EXPOSURES_DIR,
    DATA_HAZARDS_DIR,
    DATASETS_DIR,
    EEA_COUNTRIES,
    FEATHERS_DIR,
    LIST_OF_RCPS,
    MAP_DIR,
    REQUIREMENTS_DIR,
    SHAPEFILES_01M_FILE,
    TEMP_DIR,
    THREE_LETTER_EUROPEAN_EXPOSURE,
)
from logger_config import LoggerConfig

logger = LoggerConfig(logger_types=["file"])

# EXPOSURE METHODS DEFINITION


def get_exposure_dataset_infos(countries: list) -> DatasetInfo:
    """
    Find all datasets matching the given parameters.

    Parameters
    ----------
    countries : list, required
        List of country names for which to search for datasets.

        Example: ['Greece', 'Bulgaria', 'Slovenia']

    Returns
    -------
    DatasetInfo
    """
    try:
        client = Client()
        exposure_dataset_infos = client.list_dataset_infos(
            data_type="litpop",
            properties={
                "country_name": countries,
                "exponents": "(1,1)",
                "fin_mode": "pc",
            },
        )
        if not exposure_dataset_infos:
            raise ValueError("No exposure datasets found.")

        return exposure_dataset_infos

    except Exception as exc:
        status_message = f"Error while trying to fetch exposure dataset_infos. {exc}"
        raise ValueError(status_message)


def get_exposure(countries: list) -> Exposures:
    """
    Query the data api for exposures datasets of the given type, download associated
    hdf5 files and turn them into a climada.entity.exposures.Exposures object.

    Parameters
    ----------
    countries : list, required
        List of country names for which to create the LitPop object.

        Example: ['Greece', 'Bulgaria', 'Slovenia']

    Returns
    -------
    exposure : Exposures
        climada.entity.exposures.base.Exposures
    """
    start_time = time()
    # print("Start fetching exposures from client...")
    client = Client()

    exposures_list = []
    exposure_dataset_infos = get_exposure_dataset_infos(countries)

    for dataset in exposure_dataset_infos:
        exposure_filename = dataset.files[
            0
        ].file_name  # needs to be revisited in case dataset consists of multiple files in the future
        exposure_filepath = Path(DATA_EXPOSURES_DIR, exposure_filename)
        exposure_properties = dataset.properties
        country = exposure_properties["country_name"]
        # if the file exists in the exposures directory, the Exposures object is created
        # from this file.
        if path.exists(exposure_filepath):
            # print(
            #     f"File {exposure_filename} already exists and will be used to create Exposures object."
            # )
            exposure = Exposures.from_hdf5(exposure_filepath)

        # if the file does not exist in the exposures directory, the default litpop file
        # for this country will be downloaded and stored in the exposures directory.
        else:
            # print(f"File {exposure_filename} does not exists and will be downloaded.")
            exposure = client.get_exposures(
                exposures_type="litpop",
                properties=exposure_properties,
                dump_dir=exposure_filepath,
            )

        currency_convert_ratio = get_currency_rates()
        exposure.value_unit = "EUR"
        exposure_gdf = exposure.gdf
        exposure_gdf["value"] = exposure_gdf["value"] / currency_convert_ratio  # Convert USD to EUR
        exposure_gdf_weighted = assign_coords_and_weights(countries=[country])
        gdf = pd.merge(exposure_gdf, exposure_gdf_weighted, how="inner", on="geometry")
        gdf.drop(
            columns=["latitude_y", "longitude_y", "impf_", "region_id"],
            axis=1,
            inplace=True,
        )
        gdf.rename(columns={"latitude_x": "latitude", "longitude_x": "longitude"}, inplace=True)
        exposure.set_gdf(gdf)
        exposures_list.append(exposure)

    exposures = Exposures.concat(exposures_list)
    exposures.tag.description = f"LitPop Exposure for {', '.join(countries)}"
    exposures.tag.file_name = exposure_filename
    # print(f"Finished fetching exposures from client in {time() - start_time}sec.")

    return exposures


def get_exposure_new(country: str) -> Exposures:
    start_time = time()
    client = Client()
    try:
        exposure = client.get_litpop(
            country=country, exponents=(1, 1), dump_dir=Path(DATA_EXPOSURES_DIR)
        )
        status_message = f"Finished fetching exposure from client in {time() - start_time}sec."
        logger.log("debug", status_message)
        return exposure

    except Exception as exc:
        status_message = f"Error while trying to fetch exposure for {country}. More info: {exc}"
        logger.log("debug", status_message)
        raise ValueError(status_message)


def generate_exposure_geojson(exposure: Exposures, country_name: str):
    try:
        exposure_gdf = exposure.gdf
        country_iso3 = get_iso3_country_code(country_name)

        GADM41_filename = Path(REQUIREMENTS_DIR) / f"gadm41_{country_iso3}.gpkg"
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
                logger.log("debug", f"File not found: {GADM41_filename}")
            except Exception as e:
                logger.log("debug", f"An error occurred while processing layer {layer}: {e}")

        # Save the combined GeoJSON file
        map_data_filepath = MAP_DIR / "exposures_geodata.json"
        with open(map_data_filepath, "w") as f:
            json.dump(all_layers_geojson, f)

    except AttributeError as e:
        logger.log("debug", f"Invalid Exposure object: {e}")
    except Exception as e:
        logger.log("debug", f"An unexpected error occurred: {e}")


def get_iso3_country_code(country_name: str) -> str:
    try:
        country = pycountry.countries.search_fuzzy(country_name)[0]
        return country.alpha_3
    except LookupError:
        print(f"No ISO3 code found for '{country_name}'. Please check the country name.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def get_exposure_data_from_xlsx(filepath: str) -> pd.DataFrame:
    """
    Read the selected .xlsx input file and build the necessary exposure data to
    create an Exposures object.

    Parameters
    ----------
    filepath : str, required
        File path of the .xlsx input file. The file must be placed in the data/exposures folder.

    Returns
    -------
    exposure_data : pandas.Dataframe
    """
    try:
        df_unsanitized = pd.read_excel(path.join(DATA_EXPOSURES_DIR, filepath))
        df = sanitize_exposure_xlsx(df_unsanitized)
        exposure_xlsx_category = get_exposure_xlsx_category(df.columns)

        if exposure_xlsx_category in ["country", "nuts2"]:
            # print(f"Assigning weighted values to disaggregated coordinates...")
            if exposure_xlsx_category == "country":
                countries = df["country"].unique()
                df_assigned = assign_coords_and_weights(countries=list(countries))
                exposure_data = pd.merge(df_assigned, df, on=["country", "country"])

            if exposure_xlsx_category == "nuts2":
                nuts2 = df["nuts2"].unique()
                df_assigned = assign_coords_and_weights(nuts2=list(nuts2))
                exposure_data = pd.merge(df_assigned, df, on=["nuts2", "nuts2"])

            exposure_data["weighted_value"] = exposure_data["weight"] * exposure_data["value"]
            exposure_data.drop(columns=["value", "weight"], inplace=True, axis=1)
            exposure_data.rename(columns={"weighted_value": "value"}, inplace=True)
            exposure_data = exposure_data.dropna(axis=0)
        else:
            polygons = get_polygons([])
            df["geometry"] = gpd.points_from_xy(df["longitude"], df["latitude"])
            points = gpd.GeoDataFrame(df, geometry="geometry", crs=polygons.crs)
            exposure_data = sjoin(points, polygons, predicate="within", how="left")
            exposure_data.drop(["index_right"], inplace=True, axis=1)

        exposure_data = exposure_data.dropna(axis=0)
        exposure_data.reset_index(drop=True, inplace=True)
    except Exception as exc:
        # print(f"Failed to match exposure data. More info: {exc}")
        return None

    return exposure_data


def get_exposure_from_xlsx(filepath: str) -> Exposures:
    """
    Read the selected .xlsx input file and create a climada.entity.exposures.Exposures object.

    Parameters
    ----------
    filepath : str, required
        File path of the .xlsx input file. The file must be placed in the data/exposures folder.

    Returns
    -------
    exposure : Exposures
        climada.entity.exposures.base.Exposures
    """
    start_time = time()
    # print("Start creating exposures from xlsx...")

    try:
        exposure_data = get_exposure_data_from_xlsx(filepath)
        group_by_country = exposure_data.groupby(["country"])
        countries = list(group_by_country.groups.keys())
        exposure = Exposures(exposure_data)
        exposure.tag.description = f"LitPop Exposure for {', '.join(countries)}"
        exposure.tag.file_name = path.basename(filepath)
    except Exception as exc:
        # print(f"Failed to match coordinates to countries. More info: {exc}")
        return None

    # print(f"Finished creating exposures from xlsx in {time() - start_time}sec.")
    return exposure


def get_countries_from_exposure_xlsx(filepath: str) -> list:
    """
    Read the selected .xlsx input file and get the distinct countries from the coordinates,
    nuts2 or countries.

    Parameters
    ----------
    filepath : str, required
        File path of the .xlsx input file. The file must be placed in the data/exposures folder.

    Returns
    -------
    countries : list
        list of countries
    """
    start_time = time()
    # print("Start matching countries from xlsx exposures...")

    countries = []
    exposure_data = get_exposure_data_from_xlsx(filepath)

    try:
        group_by_country = exposure_data.groupby(["country"])
        countries = list(group_by_country.groups.keys())
    except Exception as exc:
        # print(f"Failed to match coordinates to countries. More info: {exc}")
        pass
    # print(
    #     f"Finished matching countries from xlsx exposures in {time() - start_time}sec."
    # )

    return countries


def get_exposure_xlsx_category(columns: list) -> str:
    """
    Get the category of the ipnut .xlsx file. Options are:
        - File with lat/long coordinates.
        - File with nuts2 level exposure.
        - File with country level exposure.

    Parameters
    ----------
    columns : list, required
        List of .xlsx columns.

    Returns
    -------
    category : str
        Type of .xlsx input file based on the exposure type (coords, nuts2 or country)
    """
    nuts2_columns = ["nuts2", "value"]
    country_columns = ["country", "value"]
    coords_columns = ["latitude", "longitude", "value"]

    if all(item in columns for item in coords_columns):
        return "coords"
    if all(item in columns for item in nuts2_columns):
        return "nuts2"
    if all(item in columns for item in country_columns):
        return "country"
    return "error"


def sanitize_exposure_xlsx(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize the structure of the exposure .xlsx input file.

    Parameters
    ----------
    df : pandas.DataFrame, required
        pandas.DataFrame with the .xlsx exposure input data.

    Returns
    -------
    df : pandas.DataFrame
        pandas.DataFrame with the sanitized .xlsx exposure input data.
    """
    try:
        # Clear rows with missing values
        df = df.dropna()
        columns = list(df.columns)

        # Change column names to follow conventions
        for column in columns:
            if column.lower() in ["nuts2", "nuts"]:
                df.rename(columns={column: "nuts2"}, inplace=True)
            if column.lower() in ["latitude", "lat"]:
                df.rename(columns={column: "latitude"}, inplace=True)
            if column.lower() in ["longitude", "long"]:
                df.rename(columns={column: "longitude"}, inplace=True)
            if column.lower() in ["country", "cntr"]:
                df.rename(columns={column: "country"}, inplace=True)
            if column.lower() in ["value", "values", "loss", "losses"]:
                df.rename(columns={column: "value"}, inplace=True)

        # Add weight and weighted values columns.
        sanitized_columns = list(df.columns)

        exposure_xlsx_category = get_exposure_xlsx_category(sanitized_columns)
        if exposure_xlsx_category == "coords":
            df = df[["latitude", "longitude", "value"]]
        if exposure_xlsx_category == "nuts2":
            df = df[["nuts2", "value"]]
        if exposure_xlsx_category == "country":
            df = df[["country", "value"]]
        if exposure_xlsx_category == "error":
            raise Exception("Required columns are missing")

    except Exception as exc:
        # print(f"Error while trying to parse xlsx input file. More info: {exc}")
        pass
    return df


def assign_coords_and_weights(nuts2: list = [], countries: list = []) -> pd.DataFrame:
    """
    Reads the feather files to get the exposure geodataframe data.

    Parameters
    ----------
    nuts2 : list, optional
        List of nuts2 level exposure.
    countries : list, optional
        List of country level exposure.

    Returns
    -------
    exposure_gdf : pandas.DataFrame
        pandas.DataFrame with the exposure geodataframe data.
    """
    if nuts2 and not countries:
        exposure_gdf = gpd.read_feather(Path(FEATHERS_DIR, "eea_exposures_nuts2_gdf.feather"))
        exposure_gdf = exposure_gdf[exposure_gdf["nuts2"].isin(nuts2)]
    if countries and not nuts2:
        exposure_gdf = gpd.read_feather(Path(FEATHERS_DIR, "eea_exposures_countries_gdf.feather"))
        exposure_gdf = exposure_gdf[exposure_gdf["country"].isin(countries)]

    exposure_gdf.reset_index(drop=True, inplace=True)
    return exposure_gdf


def get_polygons(countries: list) -> gpd.GeoDataFrame:
    """
    Sanitize the Eurostat shapefiles to include only relevant countries and nuts2
    level administrations. More info:
    https://ec.europa.eu/eurostat/web/gisco/geodata/reference-data/administrative-units-statistical-units/countries

    Parameters
    ----------
    countries : list, required
        List of country names.

        Example: ['Italy', 'Switzerland']

    Returns
    -------
    GeoPandas.GeoDataFrame.
    """
    # Read shapefile into GeoDataFrame object.
    polygons = gpd.GeoDataFrame.from_file(SHAPEFILES_01M_FILE)

    # Filter out non nuts2 level coordinates.
    polygons = polygons[polygons["LEVL_CODE"] == 2]

    # Rename country codes to match pycountry country codes
    polygons["CNTR_CODE"] = polygons["CNTR_CODE"].replace({"EL": "GR"})
    polygons["CNTR_CODE"] = polygons["CNTR_CODE"].replace({"UK": "GB"})

    # Keep specific columns and match country codes to counteis
    polygons = polygons[["NUTS_ID", "CNTR_CODE", "NAME_LATN", "geometry"]].reset_index(drop=True)
    polygons["CNTR_CODE"] = polygons["CNTR_CODE"].apply(
        lambda country_code: pycountry.countries.get(alpha_2=country_code).name
    )

    # Rename columns
    polygons = polygons[["CNTR_CODE", "NUTS_ID", "NAME_LATN", "geometry"]]
    polygons.columns = ["country", "nuts2", "nuts_description", "geometry"]

    # Filter out non eea countries
    polygons = polygons[polygons["country"].isin(EEA_COUNTRIES)]

    # Return specific countries if provides, else only EEA
    if countries:
        polygons = polygons[polygons["country"].isin(countries)]

    return polygons


def convert_iso2_to_iso3(iso2_code: str):
    if iso2_code == "EL":
        iso2_code = "GR"
    if iso2_code == "UK":
        iso2_code = "GB"
    try:
        iso3_code = pycountry.countries.get(alpha_2=iso2_code).alpha_3
        return iso3_code
    except Exception as exc:
        # print(
        #     f"Error while trying to convert iso2 code {iso2_code} to iso3 code. More info: {exc}"
        # )
        return ""


def get_country_name_from_country_code(country_code: str) -> str:
    """
    Returns the name of the country associated with the given country code.

    Parameters
    ----------
    country_code : str
        The country code to be used to look up the country name, either a two-letter code (ISO 3166-1 alpha-2) or a three-letter code (ISO 3166-1 alpha-3).

    Returns
    -------
    country_name : str
        The name of the country associated with the given country code, as a string.

    Notes
    -----
    If the country code is a two-letter code (ISO 3166-1 alpha-2), it will first be converted to its equivalent three-letter code (ISO 3166-1 alpha-3) using the following mappings:
        - 'EL' is mapped to 'GR'
        - 'UK' is mapped to 'GB'

    If an error occurs while trying to look up the country name, a message will be printed to the console indicating the error, but the function will still return an empty string.
    """
    country_name = ""
    try:
        if len(country_code) == 2:
            if country_code == "EL":
                country_code = "GR"
            if country_code == "UK":
                country_code = "GB"
            country_name = pycountry.countries.get(alpha_2=country_code).name
        if len(country_code) == 3:
            country_name = pycountry.countries.get(alpha_3=country_code).name
    except Exception as exc:
        # print(
        #     f"Error while trying to get the country name from country code {country_code}. More info: {exc}"
        # )
        pass
    return country_name


def get_eea_country_codes() -> list:
    """
    Returns a list of two-letter ISO country codes for the countries that are members of the European
    Economic Area (EEA).

    Parameters
    ----------
        None.

    Returns
    -------
        - A list of two-letter ISO country codes (strings) for the EEA member countries.

    Examples
    --------
        >>> get_eea_country_codes()
        ['AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HR', 'HU', 'IE', 'IS', 'IT',         'LI', 'LT', 'LU', 'LV', 'MT', 'NL', 'NO', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK', 'UK']

    Notes
    -----
        - This function requires the `pycountry` package to be installed.
        - The function uses a list of EEA country names (defined in the `EEA_COUNTRIES` constant) to look up the
          corresponding two-letter ISO country codes using the `pycountry` module.
        - The resulting list of country codes is then modified to replace the country code 'GR' with 'EL' (which is
          the ISO country code used for Greece in the EEA), and the country code 'GB' with 'UK' (which is the ISO
          country code used for the United Kingdom in the EEA).
        - If an error occurs while trying to get the country codes, an error message will be printed and an empty list
          will be returned.
    """
    eea_country_codes = []
    try:
        eea_country_codes = [pycountry.countries.search_fuzzy(c)[0].alpha_2 for c in EEA_COUNTRIES]
        eea_country_codes = [
            "EL" if code == "GR" else "UK" if code == "GB" else code for code in eea_country_codes
        ]
    except Exception as exc:
        # print(
        #     f"Error while trying to get the country codes from country names. More info: {exc}"
        # )
        pass
    return eea_country_codes


def get_country_country_codes_from_country_names(countries: list):
    country_codes = []
    try:
        for country_name in countries:
            country_code = pycountry.countries.search_fuzzy(country_name)[0].alpha_2
            country_codes.append(country_code)
        country_codes = [
            "EL" if code == "GR" else "UK" if code == "GB" else code for code in country_codes
        ]
    except Exception as exception:
        # print(
        #     f"Exception while getting country codes from country names. More info: {exception}"
        # )
        pass
    return country_codes


def convert_exposure_to_gdf(exposure_type: str = "litpop") -> gpd.GeoDataFrame:
    """
    Convert exposure datasets to a GeoDataFrame.

    Parameters
    ----------
    exposure_type (str): type of exposure data. Default is 'litpop'.

    Returns
    -------
    GeoDataFrame: a GeoDataFrame that contains the exposure data along with
    information about the country, NUTS1, NUTS2, and NUTS3 regions where the
    exposure occurs.

    Notes
    -----
    - The method uses the eurostat shapefiles and performs a spatial join between
    the exposure data and the shapefiles to add information about the country, NUTS1,
    NUTS2, and NUTS3 regions where the exposure occurs.
    - The method calculates the weighted values for the exposure data on the country,
    NUTS1, NUTS2, and NUTS3 levels.
    - The method saves the final GeoDataFrame to a feather file 'europe_gdf.feather'.
    """
    try:
        client = Client()
        if exposure_type == "litpop":
            eurostat_shapefile = gpd.read_file(SHAPEFILES_01M_FILE)

            EEA_COUNTRIES_CODES = get_eea_country_codes()
            eurostat_shapefile = eurostat_shapefile[
                eurostat_shapefile["CNTR_CODE"].isin(EEA_COUNTRIES_CODES)
            ].reset_index(drop=True)

            # Add polygons column to preserve the original Polygons/Multipolygons information
            eurostat_shapefile["polygons"] = eurostat_shapefile["geometry"]
            country_codes_iso2 = eurostat_shapefile.CNTR_CODE.unique()
            exp_gdf_list = []
            for country_code_iso2 in country_codes_iso2:
                country_code_iso3 = convert_iso2_to_iso3(country_code_iso2)
                exp_gdf = client.get_exposures(
                    exposures_type="litpop",
                    properties={
                        "country_iso3alpha": country_code_iso3,
                        "exponents": "(1,1)",
                    },
                    dump_dir=Path(DATA_EXPOSURES_DIR),
                ).gdf

                # Perform a spatial join
                merged = gpd.sjoin(
                    exp_gdf,
                    eurostat_shapefile[eurostat_shapefile["LEVL_CODE"] == 0],
                    how="inner",
                    predicate="within",
                )
                exp_gdf["country_code"] = merged["CNTR_CODE"]
                exp_gdf["country_name"] = merged["CNTR_CODE"].apply(
                    lambda c: get_country_name_from_country_code(c)
                )
                merged = gpd.sjoin(
                    exp_gdf,
                    eurostat_shapefile[eurostat_shapefile["LEVL_CODE"] == 1],
                    how="inner",
                    predicate="within",
                )
                exp_gdf["nuts1_code"] = merged["NUTS_ID"]
                exp_gdf["nuts1_name"] = merged["NAME_LATN"]
                merged = gpd.sjoin(
                    exp_gdf,
                    eurostat_shapefile[eurostat_shapefile["LEVL_CODE"] == 2],
                    how="inner",
                    predicate="within",
                )
                exp_gdf["nuts2_code"] = merged["NUTS_ID"]
                exp_gdf["nuts2_name"] = merged["NAME_LATN"]
                merged = gpd.sjoin(
                    exp_gdf,
                    eurostat_shapefile[eurostat_shapefile["LEVL_CODE"] == 3],
                    how="inner",
                    predicate="within",
                )
                exp_gdf["nuts3_code"] = merged["NUTS_ID"]
                exp_gdf["nuts3_name"] = merged["NAME_LATN"]

                # Filter out points that are inside neighbouring countries.
                exp_gdf = exp_gdf[exp_gdf["country_code"] == country_code_iso2]

                # Calculate weighted values on country level
                exp_gdf["sum_value_country"] = exp_gdf.groupby(["country_code"])["value"].transform(
                    "sum"
                )
                exp_gdf["weight_country"] = exp_gdf["value"] / exp_gdf["sum_value_country"]
                # Calculate weighted values on nuts1 level
                exp_gdf["sum_value_nuts1"] = exp_gdf.groupby(["nuts1_code"])["value"].transform(
                    "sum"
                )
                exp_gdf["weight_nuts1"] = exp_gdf["value"] / exp_gdf["sum_value_nuts1"]
                # Calculate weighted values on nuts2 level
                exp_gdf["sum_value_nuts2"] = exp_gdf.groupby(["nuts2_code"])["value"].transform(
                    "sum"
                )
                exp_gdf["weight_nuts2"] = exp_gdf["value"] / exp_gdf["sum_value_nuts2"]
                # Calculate weighted values on nuts3 level
                exp_gdf["sum_value_nuts3"] = exp_gdf.groupby(["nuts3_code"])["value"].transform(
                    "sum"
                )
                exp_gdf["weight_nuts3"] = exp_gdf["value"] / exp_gdf["sum_value_nuts3"]
                exp_gdf.drop(
                    columns=[
                        "sum_value_country",
                        "sum_value_nuts1",
                        "sum_value_nuts2",
                        "sum_value_nuts3",
                    ],
                    axis=1,
                    inplace=True,
                )

                # Add exp_gdf DataFrame to exp_gdf_list
                exp_gdf_list.append(exp_gdf)

        merged_gdf = gpd.GeoDataFrame(pd.concat(exp_gdf_list))
        merged_gdf.reset_index(inplace=True, drop=True)
        merged_gdf.to_feather(Path(FEATHERS_DIR, "europe_gdf.feather"))

        return merged_gdf
    except Exception as exc:
        # print(f"Error while trying to convert exposures to gdf. More info {exc}")
        pass


def get_country_from_country_code(country_code: str) -> str:
    """
    Get the country name from the country's iso2 code.

    Parameters
    ----------
    country_code : str, required
        ISO2 Country code

        Example: 'IT', 'GR'

    Returns
    -------
    country: str
        Country name.
    """
    country = pycountry.countries.get(alpha_2=country_code).name
    return country


def get_alpha2_country_codes_from_countries(countries: list) -> list:
    """
    Get a list with countries iso2 code from a list of country names.

    Parameters
    ----------
    countries : list, required
        List of country names for which to return the country iso2 codes.

        Example: ['Italy', 'Slovenia']

    Returns
    -------
    country_codes: list
        List of country iso2 codes.

        Example: ['IT', 'SI']
    """
    country_codes = []
    try:
        for country in countries:
            country_code = pycountry.countries.get(name=country).alpha_2
            country_codes.append(country_code)
    except Exception as exc:
        # print(f"Error while tring to match countries to alpha2 codes. More info: {exc}")
        pass
    return country_codes


def __assign_country_weights_to_eea_countries__():
    """
    Assign weight to EEA countries and store GeoDataFrame data to feather file.

    Parameters
    ----------

    Returns
    -------

    """
    polygons = get_polygons([])
    exposure_gdf_raw = get_exposure(list(EEA_COUNTRIES)).gdf
    points = sjoin(exposure_gdf_raw, polygons, predicate="within", how="left")
    points = points.dropna(axis=0).reset_index(drop=True)
    points["sum_value"] = points.groupby(["country"])["value"].transform("sum")
    points["weight"] = points["value"] / points["sum_value"]
    points = points[
        [
            "latitude",
            "longitude",
            "geometry",
            "country",
            "nuts2",
            "nuts_description",
            "weight",
        ]
    ]
    points.to_feather(Path(FEATHERS_DIR, "eea_exposures_countries_gdf.feather"))


def __assign_nuts2_weights_to_eea_countries__():
    """
    Assign weight to EEA nuts2 administrations and store GeoDataFrame data to feather file.

    Parameters
    ----------

    Returns
    -------

    """
    polygons = get_polygons([])
    exposure_gdf_raw = get_exposure(list(EEA_COUNTRIES)).gdf
    points = sjoin(exposure_gdf_raw, polygons, predicate="within", how="left")
    points = points.dropna(axis=0).reset_index(drop=True)
    points["sum_value"] = points.groupby(["nuts2"])["value"].transform("sum")
    points["weight"] = points["value"] / points["sum_value"]
    points = points[
        [
            "latitude",
            "longitude",
            "geometry",
            "country",
            "nuts2",
            "nuts_description",
            "weight",
        ]
    ]
    points.to_feather(Path(FEATHERS_DIR, "eea_exposures_nuts2_gdf.feather"))


# HAZARD METHODS DEFINITION


def get_hazard_dataset_infos(
    hazard_type: str, countries: list, scenario: str, time_horizon: str
) -> DatasetInfo:
    """
    Find all datasets matching the given parameters.

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
    DatasetInfo
    """
    client = Client()
    if hazard_type == "tropical_cyclone":
        if scenario == "historical":
            year_prop = "tracks_year_range"
            time_horizon = "1980_2020"
        else:
            year_prop = "ref_year"

        try:
            hazard_dataset_infos = client.list_dataset_infos(
                data_type=hazard_type,
                properties={
                    "country_name": countries,
                    "climate_scenario": scenario,
                    year_prop: time_horizon,
                },
            )
        except Exception:
            # print(
            #     f"Error while trying to fetch hazard dataset_infos. Trying to fetch local data."
            # )
            dataset_infos = read_dtst_infos()
            # Filter out datasets
            dataset_infos_filtered = list(
                filter(
                    lambda dataset: dataset.properties["spatial_coverage"] == "country"
                    and dataset.version == "v2",
                    dataset_infos[hazard_type],
                )
            )

            hazard_dataset_infos = list(
                filter(
                    lambda dataset: dataset.properties["climate_scenario"] == scenario
                    and dataset.properties[year_prop] == time_horizon
                    and dataset.properties["country_name"] in countries,
                    dataset_infos_filtered,
                )
            )

    if hazard_type == "storm_europe":
        hazard_dataset_infos = client.list_dataset_infos(
            data_type=hazard_type,
            properties={
                "country_name": countries,
            },
        )

    if hazard_type == "river_flood":
        if scenario == "historical":
            time_horizon = "1980_2000"

        try:
            hazard_dataset_infos = client.list_dataset_infos(
                data_type=hazard_type,
                properties={
                    "country_name": countries,
                    "climate_scenario": scenario,
                    "year_range": time_horizon,
                },
            )
        except Exception:
            # print(
            #     f"Error while trying to fetch hazard dataset_infos. Trying to fetch local data."
            # )
            dataset_infos = read_dtst_infos()
            # Filter out datasets
            dataset_infos_filtered = list(
                filter(
                    lambda dataset: dataset.properties["spatial_coverage"] == "country"
                    and dataset.version == "v2",
                    dataset_infos[hazard_type],
                )
            )

            hazard_dataset_infos = list(
                filter(
                    lambda dataset: dataset.properties["climate_scenario"] == scenario
                    and dataset.properties["year_range"] == time_horizon
                    and dataset.properties["country_name"] in countries,
                    dataset_infos_filtered,
                )
            )

    if not hazard_dataset_infos:
        raise ValueError("No hazard datasets found.")

    return hazard_dataset_infos


def get_hazard(hazard_type: str, scenario: str, time_horizon: str, countries: list) -> Hazard:
    """
    Queries the data api for hazard datasets of the given type, downloads associated
    hdf5 files and turns them into a climada.hazard.Hazard object.

    Parameters
    ----------
    hazard_type: str, required
        Hazard type to search datasets.
        Example: river_flood, tropical_cyclone, storm_europe.
    scenario: str, required
        Type of scenario to search datasets.
        Example: historical, rcp26, rcp45 etc.
    time_horizon: str, required
        Time horizon to search datasets.
        Example: 1980-2000, 2030-2050 etc.
    countries: list, required
        List of country names for which to search for datasets.
        Example: ['Greece', 'Bulgaria', 'Slovenia']

    Returns
    -------
    hazard: climada.hazard.Hazard
        The combined hazard object.
    """
    start_time = time()
    # print("Start fetching hazards from client...")
    hazards = []
    try:
        client = Client()
        hazard_dataset_infos = get_hazard_dataset_infos(
            hazard_type, countries, scenario, time_horizon
        )
        for country in countries:
            dataset = list(
                filter(
                    lambda dataset: dataset.properties["country_name"] == country,
                    hazard_dataset_infos,
                )
            )[0]
            if dataset.files:
                hazard_filename = dataset.files[
                    0
                ].file_name  # needs to be revisited in case dataset consists of multiple files in the future
            else:
                hazard_filename = f"{dataset.name}.hdf5"
            hazard_filepath = Path(DATA_HAZARDS_DIR, hazard_filename)
            hazard_properties = dataset.properties

            # if the file exists in the hazards directory, the Hazard object is created
            # from this file.
            if path.exists(hazard_filepath):
                # print(
                #     f"File {hazard_filename} already exists and will be used to create Hazard object."
                # )
                hazard = Hazard.from_hdf5(hazard_filepath)
                hazards.append(hazard)

            # if the file does not exist in the hazards directory, the hazard file
            # for this country will be downloaded and stored in the hazards directory.
            else:
                if dataset.files:
                    # print(
                    #     f"File {hazard_filename} does not exists and will be downloaded."
                    # )
                    hazard = client.get_hazard(
                        hazard_type=hazard_type,
                        properties=hazard_properties,
                        dump_dir=hazard_filepath,
                    )
                    hazards.append(hazard)
                else:
                    # print(
                    #     f"File {hazard_filename} is not available and will be excluded from Hazard object creation."
                    # )
                    pass
                continue
        hazards = Hazard.concat(hazards)
        # print(f"Finished fetching hazards from client in {time() - start_time}sec.")
        return hazards

    except Exception as exc:
        status_message = f"Error while trying to create hazard object. More info: {exc}"
        raise ValueError(status_message)


def get_hazard_new(hazard_type: str, scenario: str, time_horizon: str, country: str) -> Hazard:
    start_time = time()
    hazard_properties = {
        "country_name": country,
        "climate_scenario": scenario,
        "year_range": time_horizon,
    }
    try:
        client = Client()
        hazard = client.get_hazard(
            hazard_type=hazard_type,
            properties=hazard_properties,
            dump_dir=Path(
                DATA_HAZARDS_DIR,
            ),
        )
        status_message = f"Finished fetching hazards from client in {time() - start_time}sec."
        logger.log("debug", status_message)
        return hazard

    except Exception as exc:
        status_message = f"Error while trying to create hazard object. More info: {exc}"
        logger.log("debug", status_message)
        raise ValueError(status_message)


def mean_nonzero(series):
    non_zeros = series[series != 0]
    return non_zeros.mean() if not non_zeros.empty else 0


def generate_hazard_geojson(
    hazard: Hazard,
    country_name: str,
    return_periods: tuple = (250, 100, 50, 10),
    intensity_thres: float = None,
):
    try:
        country_iso3 = get_iso3_country_code(country_name)
        GADM41_filename = Path(REQUIREMENTS_DIR) / f"gadm41_{country_iso3}.gpkg"
        layers = [0, 1, 2]

        all_layers_geojson = {"type": "FeatureCollection", "features": []}

        if intensity_thres:
            try:
                if hazard.haz_type == "RF":
                    hazard.intensity_thres = intensity_thres
            except AttributeError as e:
                logger.log("debug", f"Attribute error in hazard object: {e}")
            except Exception as e:
                logger.log("debug", f"An unexpected error occurred: {e}")

        for layer in layers:
            admin_gdf = gpd.read_file(filename=GADM41_filename, layer=layer)

            # Assuming hazard.centroids.coord gives a list of [longitude, latitude]
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

            # Spatial join with administrative areas
            joined_gdf = gpd.sjoin(hazard_gdf, admin_gdf, how="left", predicate="within")

            # Convert to GeoJSON for this layer and add to all_layers_geojson
            layer_geojson = joined_gdf.__geo_interface__["features"]
            for feature in layer_geojson:
                feature["properties"]["layer"] = layer
                all_layers_geojson["features"].append(feature)

        # Save the combined GeoJSON file
        map_data_filepath = MAP_DIR / f"hazards_geodata.json"
        with open(map_data_filepath, "w") as f:
            json.dump(all_layers_geojson, f)
    except Exception as e:
        logger.log("debug", f"An unexpected error occurred: {e}")


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
    start_time = time()
    # print("Start creating hazard from hdf5...")
    try:
        filepath = Path(DATA_HAZARDS_DIR, filepath)
        if filepath.exists():
            print(f"File {filepath} already exists and will be used to create Hazard object.")
            hazard = Hazard.from_hdf5(filepath)

            # print(f"Finished creating hazard from hdf5 in {time() - start_time}sec.")
            return hazard
        else:
            raise FileExistsError("Hazard file not found")
    except FileExistsError as e:
        return None
    except Exception as e:
        # Handle any other exception that may occur
        return None


def get_hazard_type_from_Hazard(hazard: Hazard) -> str:
    """
    Read a Hazard object and return the hazard type.

    Parameters
    ----------
    hazard : climada.hazard.Hazard, required
        climada.hazard.Hazard object to read and extract hazard type.

    Returns
    -------
    hazard_type: str
        The hazard type of the Hazard object.
    """
    try:
        hazard_code = hazard.tag.haz_type
        if hazard_code == "WS":
            return "storm_europe"
        elif hazard_code == "TC":
            return "tropical_cyclone"
        elif hazard_code == "RF":
            return "river_flood"
        else:
            raise Exception("Hazard type not in list (storm_europe, tropical_cyclone, river_flood")
    except Exception as exc:
        status_message = f"Error while trying to match hazard type. More info: {exc}"
        raise Exception(status_message)


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

    Examples
    ---------
    Assuming `hazard_present` is a Hazard object:
        >>> scenario = get_hazard_scenario_from_Hazard(hazard_present)
        >>> print(scenario)
        >>> 'historical'

    Notes
    ------
    This method attempts to match the scenario of a given Hazard object by analyzing its file name attribute. It
    iterates through a predefined list of possible scenarios and returns the first scenario found in the file names.
    If no matching scenario is found, an empty string is returned.
    """
    # Split the file names by ';' and store them in a list
    file_names = hazard.tag.file_name.split(";")

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

    Examples
    ---------
    Assuming `hazard` is a Hazard object:
        >>> time_horizon = get_hazard_time_horizon_from_Hazard(hazard)
        >>> print(time_horizon)
        >>> ['2010-2030']

    Notes
    ------
    This method attempts to match the time horizon of a given Hazard object by analyzing its event dates.
    It iterates through a predefined list of possible year ranges and returns the first matching range
    where the minimum and maximum event dates fall within the same range.
    If no matching range is found, an empty list is returned.
    """
    try:
        scenario = get_hazard_scenario_from_Hazard(hazard)
        hazard_type = get_hazard_type_from_Hazard(hazard)

        if scenario == ["historical"]:
            if hazard_type == "storm_europe":
                return ["1940_2014"]
            if hazard_type == "river_flood":
                return ["1980_2000"]
            if hazard_type == "tropical_cyclone":
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


def get_hazard_type_from_impact(impact: Impact) -> str:
    """
    Read an Impact object and return the hazard type.

    Parameters
    ----------
    impact : climada.entity.Impact, required
        climada.entity.Impact object to read and extract the hazard type.

    Returns
    -------
    hazard_type: str
        The hazard type of the Impact object.
    """
    try:
        hazard_code = impact.tag["haz"].haz_type
        if hazard_code == "WS":
            return "storm_europe"
        elif hazard_code == "TC":
            return "tropical_cyclone"
        elif hazard_code == "RF":
            return "river_flood"
        else:
            raise Exception("Hazard type not in list (storm_europe, tropical_cyclone, river_flood")
    except Exception as exc:
        status_message = f"Error while trying to match hazard type. More info: {exc}"
        raise Exception(status_message)


def get_fields_from_hazard_file(filename: str) -> dict:
    """
    Extract scenario and time_horizon from hazard filename

    Parameters
    ----------
    exposures : list
        The exposure/s.
    filepath : str
        The full path to the hazard file.

    Returns
    -------
    data: {"scenario": str, "time_horizon": str}
    """
    try:
        fields = filename.split("_")
        if fields[0] == "river":
            if fields[3] == "hist":
                scenario = "historical"
            else:
                scenario = fields[3]
            time_horizon = f"{fields[5]}_{fields[6].split('.')[0]}"
        elif fields[0] == "WISC":
            scenario = "historical"
            time_horizon = "1940_2014"
        data = {"scenario": scenario, "time_horizon": time_horizon}
        return data
    except Exception as exception:
        # print(
        #     f"Exception while matching fields from hazard file. More info: {exception}"
        # )
        pass


def generate_hazard_gdf(hazard: Hazard, return_periods: tuple = (250, 100, 50, 10)) -> pd.DataFrame:
    """
    Generate a pandas DataFrame containing latitude, longitude, and local exceedance intensity values for the specified return periods.

    Parameters
    ----------
    hazard : Hazard
        An instance of the Hazard class containing hazard data.
    return_periods : tuple of int, optional
        A tuple containing the return periods (in years) for which to calculate local exceedance intensity values. Defaults to (25, 50, 100, 250).

    Returns
    ----------
    pandas DataFrame
        A pandas DataFrame containing latitude, longitude, and local exceedance intensity values for each return period.

    Raises:
    ----------
    ValueError
        Raised if the input hazard object is missing attributes required for the function to execute, or contains invalid data.
    Exception
        Raised if any other unexpected errors occur.

    Notes
    ----------
    The resulting DataFrame will have one row for each location in the hazard, and columns for latitude, longitude,
    and local exceedance intensity values for each return period.
    """
    start_time = time()
    try:
        # Extract the coordinates of each location in the hazard object
        coords = hazard.centroids.coord

        # Calculate the local exceedance intensity for the specified return periods
        local_exceedance_inten = hazard.local_exceedance_inten(return_periods)

        # Convert the local exceedance intensity to a pandas DataFrame and transpose it
        # This puts each location in a separate row and each return period in a separate column
        local_exceedance_inten = pd.DataFrame(local_exceedance_inten).T

        # Extract the intensity values for each return period and stack them into a NumPy array
        intensity_data = []
        for rp in return_periods:
            intensity_data.append(local_exceedance_inten.loc[rp].values.tolist())  # convert to list
        intensity_data = np.array(intensity_data)

        # Stack the coordinate values and intensity values horizontally into a NumPy array
        data = np.column_stack((coords, local_exceedance_inten))

        # Create column names for the DataFrame based on the return periods
        columns = ["latitude", "longitude"] + [f"rp{rp}" for rp in return_periods]

        # Create a pandas DataFrame from the stacked data with the specified column names
        hazard_gdf = pd.DataFrame(data, columns=columns)

        # print(f"Finished generating hazard GeoDataFrame in {time() - start_time}sec.")
        # Return the resulting DataFrame
        return hazard_gdf

    except Exception as exc:
        status_message = (
            f"An error occurred while generating the hazard geodataframe. More info: {str(exc)}"
        )
        raise ValueError(status_message)


# IMPACT METHODS DEFINITION


def calculate_impact(exposure: Exposures, hazard: Hazard, hazard_type: str) -> Impact:
    """
    Create an climada.entity.Impact object from the specified Exposures and Hazard objects.

    Parameters
    ----------
    exposure: climada.entity.exposures.Exposures, required
        Exposure object for which to calculate Impact
    hazard: climada.hazard.Hazard, required
        Hazard object for which to calculate Impact
    hazard_type: str, required
        Hazard type to search datasets.
        Example: river_flood, tropical_cyclone, storm_europe.

    Returns
    -------
    impact: climada.entity.Impact.
    """
    try:
        # Set impact function according to hazard_type
        if hazard_type == "tropical_cyclone":
            impact_function = ImpfTropCyclone.from_emanuel_usa()
            impact_function_set = ImpfSetTropCyclone.from_calibrated_regional_ImpfSet()
            impf_id = 1

        if hazard_type == "storm_europe":
            impact_function = ImpfStormEurope.from_welker()
            impact_function_set = ImpactFuncSet()
            impf_id = 1

        if hazard_type == "river_flood":
            hazard.intensity_thres = 1
            impact_function = ImpactFunc()
            impact_function.haz_type = "RF"
            impact_function.intensity_unit = "m"
            impact_function.id = 3
            impact_function.name = "Flood Europe JRC Residential"
            impact_function.intensity = np.array(
                [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 12.0]
            )
            impact_function.mdd = np.array(
                [0.00, 0.25, 0.40, 0.50, 0.60, 0.75, 0.85, 0.95, 1.00, 1.00]
            )
            impact_function.mdr = np.array(
                [0.000, 0.250, 0.400, 0.500, 0.600, 0.750, 0.850, 0.950, 1.000, 1.000]
            )
            impact_function.paa = np.ones(len(impact_function.intensity))
            impact_function_set = ImpactFuncSet()
            impf_id = 3

        # Create ImpactFuncSet object to pass to impact.calc
        impact_function_set.append(impact_function)
        exposure.gdf[f"impf_{hazard.tag.haz_type}"] = impf_id
        exposure.impact_funcs = impact_function_set
        impact = Impact()
        # Calculate impact
        impact.calc(exposure, impact_function_set, hazard, save_mat=True)

        # Reset exposure gdf columns to avoid errors when trying to reuse exposure object
        exp_gdf = exposure.gdf.drop(
            columns=[f"impf_{hazard.tag.haz_type}", f"centr_{hazard.tag.haz_type}"],
            axis=1,
        )
        exposure.set_gdf(exp_gdf)

        return impact

    except Exception as exception:
        # print("Error while trying to create Impact object. More info: ", exception)
        pass


def calculate_impact_new(exposure: Exposures, hazard: Hazard, hazard_type: str) -> Impact:
    start_time = time()
    try:
        # Set impact function according to hazard_type
        if hazard_type == "tropical_cyclone":
            impact_function = ImpfTropCyclone.from_emanuel_usa()
            impact_function_set = ImpfSetTropCyclone.from_calibrated_regional_ImpfSet()
            impf_id = 1
        # TODO: Adjust this for Asia/Africa
        if hazard_type == "river_flood":
            hazard.intensity_thres = 1
            impact_function = ImpactFunc()
            impact_function.haz_type = "RF"
            impact_function.intensity_unit = "m"
            impact_function.id = 3
            impact_function.name = "Flood Europe JRC Residential"
            impact_function.intensity = np.array(
                [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 12.0]
            )
            impact_function.mdd = np.array(
                [0.00, 0.25, 0.40, 0.50, 0.60, 0.75, 0.85, 0.95, 1.00, 1.00]
            )
            impact_function.mdr = np.array(
                [0.000, 0.250, 0.400, 0.500, 0.600, 0.750, 0.850, 0.950, 1.000, 1.000]
            )
            impact_function.paa = np.ones(len(impact_function.intensity))
            impact_function_set = ImpactFuncSet()
            impf_id = 3

        # Create ImpactFuncSet object to pass to impact.calc
        impact_function_set.append(impact_function)
        exposure.gdf[f"impf_{hazard.haz_type}"] = impf_id
        exposure.impact_funcs = impact_function_set
        impact = Impact()
        # Calculate impact
        impact.calc(exposure, impact_function_set, hazard, save_mat=True)

        # Reset exposure gdf columns to avoid errors when trying to reuse exposure object
        exp_gdf = exposure.gdf.drop(
            columns=[f"impf_{hazard.haz_type}", f"centr_{hazard.haz_type}"],
            axis=1,
        )
        exposure.set_gdf(exp_gdf)
        status_message = f"Finished generating impact in {time() - start_time}sec."
        logger.log("debug", status_message)

        return impact

    except Exception as exception:
        status_message = (
            f"Finished generating impact in {time() - start_time}sec. More info: {exception}"
        )
        logger.log("debug", status_message)


def filter_impact_coords(impact: Impact) -> Impact:
    """
    Filters out non-european continent coordinates.

    Parameters
    ----------
    exposure: climada.entity.exposures.Exposures, required
        Exposure object for which to calculate impact data.
    impact: climada.entity.Impact, required
        Impact object for which to calculate impact data.

    Returns
    -------
    filtered_impact: Impact.
    """

    unfiltered_impact = deepcopy(impact)
    imp_coords = unfiltered_impact.coord_exp
    imp_coords_filtered = np.array(
        [
            coord
            for coord in imp_coords
            if coord[0] > 34 and coord[0] < 72 and coord[1] > -24 and coord[1] < 34
        ]
    )
    filtered_impact = unfiltered_impact.select(coord_exp=imp_coords_filtered)

    return filtered_impact


def calculate_impact_output(impact: Impact, exposure: Exposures) -> pd.DataFrame:
    """
    Create an 1-D table containing all the impact data needed to generate the reports.

    Parameters
    ----------
    exposure: climada.entity.exposures.Exposures, required
        Exposure object for which to calculate impact data.
    impact: climada.entity.Impact, required
        Impact object for which to calculate impact data.

    Returns
    -------
    impact_output: pandas.DataFrame.
    """
    initial_time = time()
    # print("Start calculating full impact output...")
    impact_matrix = impact.imp_mat.toarray()
    event_ids = np.array(impact.event_id)
    event_frequencies = np.array(impact.frequency)
    exposure_gdf = exposure.gdf

    # Calculate the Cartesian product of event_ids and exposure_gdf index
    event_indices, exposure_indices = np.meshgrid(
        np.arange(len(event_ids)), np.arange(len(exposure_gdf)), indexing="ij"
    )

    # Flatten the arrays and create a DataFrame
    data = {
        "event_id": event_ids[event_indices.ravel()],
        "geometry": exposure_gdf.geometry.values[exposure_indices.ravel()],
        "annual_rate": event_frequencies[event_indices.ravel()],
        "loss": impact_matrix.ravel(),
        "nuts2": exposure_gdf.nuts2.values[exposure_indices.ravel()],
        "nuts_description": exposure_gdf.nuts_description.values[exposure_indices.ravel()],
        "country": exposure_gdf.country.values[exposure_indices.ravel()],
    }
    impact_output = gpd.GeoDataFrame(data)

    # print(f"Finished calculating full impact output in {time()-initial_time}sec.")

    return impact_output


def calculate_impact_output_per_country(impact_output: pd.DataFrame) -> pd.DataFrame:
    """
    Get the impact result calculations in country level.

    Parameters
    ----------
    impact_output: pd.DataFrame, required
        Impact output data containing all the impact data needed to generate the reports



    Returns
    -------
    all_country_metrics: pandas.DataFrame
    """

    group_by_country = impact_output.groupby(["country"])
    calculate_country_rpl_list = [
        group_by_country.get_group(country) for country in group_by_country.groups
    ]
    all_country_metrics = {
        "RP": [],
        "sum_loss": [],
        "country": [],
    }
    all_country_metrics = pd.DataFrame(all_country_metrics)
    try:
        for country_group in calculate_country_rpl_list:
            country = country_group["country"].iloc[0]

            # Calculate the sum of losses for each event
            country_group["sum_loss"] = country_group.groupby(["event_id"])["loss"].transform("sum")
            country_group = country_group.drop_duplicates("event_id")

            # Sort sum of losses for each event from higher to lower
            country_group = country_group.sort_values("sum_loss", ascending=False).reset_index(
                drop=True
            )

            # Calculate rpl
            country_group["exceedance_probability"] = country_group["annual_rate"].cumsum()
            country_group["RP"] = 1 / country_group["exceedance_probability"]

            # Calculate rpl values
            interpolated_values = get_interp1d_value(country_group[["RP", "sum_loss"]])
            interpolated_values["RP"] = interpolated_values["RP"].apply(lambda rp: f"RPL {str(rp)}")
            interpolated_values["country"] = country

            all_country_metrics = pd.concat(
                [all_country_metrics, interpolated_values], ignore_index=True
            )

        all_country_metrics = all_country_metrics[["country", "RP", "sum_loss"]]

    except Exception as exc:
        # print(
        #     f"Error while calculating impact ouput on country level. More info: {exc}"
        # )
        pass

    return all_country_metrics


def calculate_impact_output_per_nuts2(impact: Impact) -> pd.DataFrame:
    start_time = time()
    europe_gdf = gpd.read_feather(Path(FEATHERS_DIR, "EEA_RG_01M_2021_values.feather"))
    europe_gdf = europe_gdf[europe_gdf["LEVL_CODE"] == 2]

    impact_matrix = impact.imp_mat
    annual_rate = impact.frequency[0]
    centroids = impact.coord_exp
    geometry = gpd.GeoDataFrame(
        geometry=gpd.points_from_xy(centroids[:, 1], centroids[:, 0]), crs="EPSG:4326"
    )

    imp_mat_array = impact_matrix.toarray()
    impact_df = pd.DataFrame(imp_mat_array)
    impact_df_transposed = impact_df.T

    impact_df_transposed.columns = impact.event_id
    impact_df_transposed["geometry"] = geometry
    impact_df_transposed = gpd.GeoDataFrame(
        impact_df_transposed, geometry="geometry", crs="EPSG:4326"
    )

    # perform spatial join and extract NUTS_ID values
    joined = gpd.sjoin(impact_df_transposed, europe_gdf, how="left", predicate="within")
    nuts2 = joined["NUTS_ID"]
    country_codes = joined["CNTR_CODE"]
    nuts_description = joined["NAME_LATN"]

    # add nuts2 column to impact_df_transposed
    impact_df_transposed["nuts2"] = nuts2
    impact_df_transposed["country_code"] = country_codes
    # impact_df_transposed['annual_rate'] = annual_rate
    impact_df_transposed["nuts_description"] = nuts_description
    grouped = impact_df_transposed.groupby(["nuts2"])

    all_nuts_metrics = {
        "RP": [],
        "sum_loss": [],
        "country_code": [],
        "nuts2": [],
        "nuts_description": [],
    }
    all_nuts_metrics = pd.DataFrame(all_nuts_metrics)
    try:
        for nuts2_code, group in grouped:
            country_code = group["country_code"].iloc[0]
            country = get_country_name_from_country_code(country_code)
            nuts2_name = group["nuts_description"].iloc[0]
            impact_df = group.drop(
                columns=["geometry", "nuts2", "country_code", "nuts_description"]
            )
            impact_df = impact_df.T
            impact_df["sum_loss"] = impact_df.sum(axis=1)
            impact_df["annual_rate"] = annual_rate
            impact_df = impact_df[["sum_loss", "annual_rate"]]
            impact_df = impact_df.sort_values("sum_loss", ascending=False).reset_index(drop=True)
            # Calculate rpl
            impact_df["exceedance_probability"] = impact_df["annual_rate"].cumsum()
            impact_df["RP"] = 1 / impact_df["exceedance_probability"]
            # Calculate rpl values
            interpolated_values = get_interp1d_value(impact_df[["RP", "sum_loss"]])
            interpolated_values["RP"] = interpolated_values["RP"].apply(lambda rp: f"RPL {str(rp)}")
            interpolated_values["country"] = country
            interpolated_values["nuts2"] = nuts2_code
            interpolated_values["nuts_description"] = nuts2_name
            all_nuts_metrics = pd.concat([all_nuts_metrics, interpolated_values], ignore_index=True)

        all_nuts_metrics = all_nuts_metrics[
            ["country", "nuts2", "nuts_description", "RP", "sum_loss"]
        ]
    except Exception as exc:
        # print(f"Error while calculating impact ouput on nuts2 level. More info: {exc}")
        pass
    # print(
    #     f"Finished calculating full impact output in nuts2 level in {time()-start_time}sec."
    # )
    return all_nuts_metrics


def get_impact_function_from_impact(impact: Impact) -> str:
    """
    Get the impact function of an climada.entity.Impact object.

    Parameters
    ----------
    impact: climada.entity.Impact, required
        Impact object to get impact function.

    Returns
    -------
    str
    """
    hazard_code = impact.tag["haz"].haz_type

    if hazard_code == "WS":
        return "Welker 2021"
    if hazard_code == "TC":
        return "Kerry Emanuel 2011"
    if hazard_code == "RF":
        return "Flood Europe JRC Residential"


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
        # print(f"Error while trying to interpolate values. More info: {exc}")
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


def set_map_title(hazard_type: str, countries: list, time_horizon: str, scenario: str) -> str:
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
    countries_stringified = ", ".join(countries)
    scenario_beautified = beautify_scenario(scenario)
    time_horizon_beautified = beautify_time_horizon(time_horizon)

    if scenario == "historical":
        map_title = f"{hazard_beautified} risk analysis for {countries_stringified} in {time_horizon_beautified} ({scenario_beautified} scenario)."
    else:
        map_title = f"{hazard_beautified} risk analysis for {countries_stringified} in {time_horizon_beautified} (scenario {scenario_beautified})."
    return map_title


def get_currency_rates() -> float:
    """
    Get the currency rates of EUR compared to USD.

    Parameters
    ----------

    Returns
    -------
    euro_rate: float
        The EUR rate compared to USD.
    """
    euro_rate = 1
    try:
        with open(CURRENCY_RATES, "r") as file:
            data = json.load(file)
            euro_rate = data["rates"]["EUR"]
    except Exception as exc:
        raise Exception(f"Error while trying to get currency rates. More info: {exc}")

    return euro_rate


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


def get_ref_year(hazard_type: str, time_horizon: str) -> int:
    if hazard_type == "river_flood":
        if time_horizon == "2010_2030":
            return 2020
        if time_horizon == "2030_2050":
            return 2040
        if time_horizon == "2050_2070":
            return 2060
        if time_horizon == "2070_2090":
            return 2080
    if hazard_type == "tropical_cyclone":
        return int(time_horizon)


def compare_values(value_present: float, value_future: float):
    """
    Helper method to compare present and future values and return
    the difference percentage.

    Parameters
    ----------
    value_present: float, required
        Present value
    value_future: float, required
        Future value

    Returns
    -------
    float or N/A
    """
    if value_present == 0 and value_future == 0:
        return "N/A"
    if value_present == 0 and value_future != 0:
        return 1
    if value_present != 0 and value_future == 0:
        return "N/A"
    else:
        return (value_future - value_present) / value_present


def clear_temp_dir():
    """
    Clear all helper temp files from the temp directory.

    Parameters
    ----------

    Returns
    -------

    """
    path = Path(TEMP_DIR)
    try:
        for file in path.glob("*"):
            Path(path, file).unlink(missing_ok=True)
    except Exception as exc:
        # print(f"Error while trying to clear temp directort. More info: {exc}")
        pass


def clear_map_images():
    """
    Clear all map image files from the assets directory.

    Parameters
    ----------

    Returns
    -------

    """
    try:
        path = Path(CLIENT_ASSETS_DIR)
        for file in path.glob("*"):
            # Clear hazard, impact and exposure previously generated maps
            if file.name.startswith(("hazard_", "impact_", "exposure_")):
                Path(path, file).unlink(missing_ok=True)
    except Exception as exc:
        # print(f"Error while trying to clear temp directort. More info: {exc}")
        pass


# TO BE REFACTORED


def get_fields_from_h5(exposures: list, hazard_file: str) -> dict:
    """
    Return a dictionary object holding the data, result and message information which will be the
    response after json convertion in the api call function that will use the current method.

    Parameters
    ----------
    exposures : list
        The exposure/s.
    hazard_file : str
        The full path to the hazard file.

    Returns
    -------
    data
        The dictionary object holding the data (dict), status (dict) information.
    """
    # Try to read the imported file with the method 'Hazard.from_hdf5'.
    try:
        haz = Hazard.from_hdf5(path.join(DATA_HAZARDS_DIR, hazard_file))
        haz.check()
    except:
        data = {
            "data": {},
            "status": {
                "code": 3001,
                "message": "Could not load Input Hazard file with Hazard.from_hdf5 method.",
            },
        }
        return data
    # Description: The purpose of the Logic implemented below is to validate
    # if the exposure of the imported hazard file is included in the selected/
    # imported exposures by the users and also to extract a) the hazard type,
    # b) the climate scenario and c) the time horizon of the file.
    try:
        hazard = ""
        scenario = ""
        # Find hazard type from climada.hazard.base.Hazard object.
        if haz.tag.haz_type == "TC":
            # Check if the exposure of the hazard file imported is not in
            # the list of exposures selected or loaded in the previous step.
            hazard = "tropical_cyclone"
            flag = True
            if (
                hazard_file.split(".")[0].count("_") in [6, 7]
                and "10synth_tracks_150arcsec" in hazard_file.split(".")[0]
            ):
                exposure = ""
                for key in THREE_LETTER_EUROPEAN_EXPOSURE.keys():
                    if key in hazard_file.split(".")[0]:
                        exposure = key

                scenario = ""
                if exposure == "" or THREE_LETTER_EUROPEAN_EXPOSURE[exposure] not in exposures:
                    data = {
                        "data": {},
                        "status": {
                            "code": 4001,
                            "message": "Exposure of hazard file not in list of selected/imported exposures.",
                        },
                    }
                    return data
                else:
                    for rcp in LIST_OF_RCPS:
                        if rcp in hazard_file.split(".")[0]:
                            scenario = rcp

                if scenario == "":
                    scenario = "historical"

                time_horizon = ""
                if scenario == "historical":
                    try:
                        if hazard_file.split(".")[0].split("_")[-1] == "2020":
                            time_horizon = "1980_2020"
                    except:
                        flag = False
                else:
                    try:
                        if isinstance(int(hazard_file.split(".")[0].split("_")[-1]), int):
                            time_horizon = hazard_file.split(".")[0].split("_")[-1]
                    except:
                        flag = False
            else:
                # The code below would work but unfortunately the
                # hdf5 files don't hold the same information always.
                # try:
                #     if str(haz.tag).split("\n")[1][-5:] in LIST_OF_RCPS:
                #         scenario = str(haz.tag).split("\n")[1][-5:]
                #     else:
                #         scenario = "historical"
                # except:
                #     pass
                data = {
                    "data": {"scenario": "", "time_horizon": ""},
                    "status": {
                        "code": 4002,
                        # Only the hazard type field can be extracted.
                        "message": "Exposure of hazard file with unstructured file name not validated.",
                    },
                }
                return data
        elif haz.tag.haz_type == "WS":
            hazard = "storm_europe"
            flag = True
            if (
                hazard_file.split(".")[0].count("_") == 2
                and "WISC_prob_" in hazard_file.split(".")[0]
            ):
                # Check if the exposure of the hazard file imported is not in
                # the list of exposures selected or loaded in the previous step.
                if THREE_LETTER_EUROPEAN_EXPOSURE[hazard_file.split(".")[0][-3:]] not in exposures:
                    data = {
                        "data": {},
                        "status": {
                            "code": 4001,
                            "message": "Exposure of hazard file not in list of selected/imported exposures.",
                        },
                    }
                    return data
                else:
                    scenario = "historical"
                    time_horizon = "1940_2014"
            else:
                data = {
                    "data": {},
                    "status": {
                        "code": 4002,
                        # Only the hazard type field can be extracted.
                        "message": "Exposure of hazard file with unstructured file name not validated.",
                    },
                }
                return data
        elif haz.tag.haz_type == "RF":
            hazard = "river_flood"
            flag = True
            if (
                hazard_file.split(".")[0].count("_") == 6
                and "river_flood_150arcsec_" in hazard_file.split(".")[0]
            ):
                exposure = ""
                for key in THREE_LETTER_EUROPEAN_EXPOSURE.keys():
                    if key in hazard_file.split(".")[0]:
                        exposure = key

                scenario = ""
                if exposure == "" or THREE_LETTER_EUROPEAN_EXPOSURE[exposure] not in exposures:
                    data = {
                        "data": {},
                        "status": {
                            "code": 4001,
                            "message": "Exposure of hazard file not in list of selected/imported exposures.",
                        },
                    }
                    return data
                else:
                    for rcp in LIST_OF_RCPS:
                        if rcp in hazard_file.split(".")[0]:
                            scenario = rcp

                if scenario == "":
                    scenario = "historical"

                time_horizon = ""
                if scenario == "historical":
                    try:
                        if (
                            hazard_file.split(".")[0].split("_")[-2]
                            + "_"
                            + hazard_file.split(".")[0].split("_")[-1]
                            == "1980_2000"
                        ):
                            time_horizon = "1980_2020"
                    except:
                        flag = False
                else:
                    try:
                        if (
                            hazard_file.split(".")[0].split("_")[-2]
                            + "_"
                            + hazard_file.split(".")[0].split("_")[-1]
                            == "2010_2030"
                        ):
                            time_horizon = "2010_2030"
                        elif (
                            hazard_file.split(".")[0].split("_")[-2]
                            + "_"
                            + hazard_file.split(".")[0].split("_")[-1]
                            == "2030_2050"
                        ):
                            time_horizon = "2030_2050"
                        elif (
                            hazard_file.split(".")[0].split("_")[-2]
                            + "_"
                            + hazard_file.split(".")[0].split("_")[-1]
                            == "2050_2070"
                        ):
                            time_horizon = "2050_2070"
                        elif (
                            hazard_file.split(".")[0].split("_")[-2]
                            + "_"
                            + hazard_file.split(".")[0].split("_")[-1]
                            == "2070_2090"
                        ):
                            time_horizon = "2070_2090"
                        else:
                            flag = False
                    except:
                        flag = False
            else:
                data = {
                    "data": {},
                    "status": {
                        "code": 4002,
                        # Only the hazard type field can be extracted.
                        "message": "Exposure of hazard file with unstructured file name not validated.",
                    },
                }
                return data
        else:
            data = {
                "data": {},
                "status": {
                    "code": 4003,
                    # Only the hazard type field can be extracted.
                    "message": "Hazard file type must have one of the following 3 values: TC, WS or RF.",
                },
            }
            return data
    except Exception as exception:
        data = {
            "data": {},
            "status": {
                "code": 4001,
                "message": "Exposure of hazard file not in list of selected/imported exposures.",
            },
        }
        return data
    if flag == True:
        data = {
            "data": {"scenario": scenario, "time_horizon": time_horizon},
            "status": {"code": 2001, "message": "All fields have been extracted."},
        }
    else:
        data = {
            "data": {"scenario": scenario, "time_horizon": time_horizon},
            "status": {
                "code": 2002,
                "message": "All fields have been extracted except from time horizon.",
            },
        }
    return data


def get_list_of_datasetInfo_objects(
    tmp_d: dict, data_type_d: dict, properties_jsonised: json, files: FileInfo
) -> DatasetInfo:
    """
    A helpful method to return the initialisation of a DatasetInfo object given the data provided
    in the parameters and to avoid code repition.

    Parameters
    ----------
    tmp_d : dict, required
        A temporary dictionary which holds information to assign values to certain DatasetInfo parameters.
    data_type_d : dict, required
        A dictionary which holds information to assign values to the required data_type parameter of the DatasetInfo object.
    properties_jsonised : json, required
        A json object to assign it to the properties parameter of the DatasetInfo object.
    files : FileInfo, required
        A FileInfo object to assign it to the files parameter of the DatasetInfo object.


    Returns
    -------
    datasetinfo_object
        An initialised DatasetInfo object.
    """
    datasetinfo_object = DatasetInfo(
        uuid=tmp_d["uuid"],
        data_type=DataTypeShortInfo(
            data_type=data_type_d["data_type"],
            data_type_group=data_type_d["data_type_group"],
        ),
        name=tmp_d["name"],
        version=tmp_d["version"],
        status=tmp_d["status"],
        properties=properties_jsonised,
        files=files,
        doi=tmp_d["doi"],
        description=tmp_d["description"],
        license=tmp_d["license"],
        activation_date=tmp_d["activation_date"],
        expiration_date=tmp_d["expiration_date"],
    )
    return datasetinfo_object


def read_dtst_infos() -> dict:
    """
    A method that reads and loads the four list_dataset_infos for the four climada hazards.

    Parameters
    ----------
    dataset_infos_filenames : list, required
        A list holding the full path filenames where the 4 list_dataset infos are stored.

    Returns
    -------
    hazard_list_dataset_infos
        A dictionary holding the four list dataset infos for the corresponding hazards.
    """

    filenames = [
        "dataset_infos_tc.txt",
        "dataset_infos_se.txt",
        "dataset_infos_rf.txt",
        "dataset_infos_rc.txt",
    ]
    dataset_infos_filenames = []

    for filename in filenames:
        dataset_infos_filenames.append(DATASETS_DIR + "\\" + filename)

    tc, se, rf, rc = ([] for _ in range(4))

    for dataset_infos_filename in dataset_infos_filenames:
        with open(dataset_infos_filename) as file:
            for idx, line in enumerate(file):
                rstripped_line = line.rstrip()
                preprocessed_line = (
                    rstripped_line.replace(" ", "")
                    .replace("{", "({")
                    .replace("}", "})")
                    .rstrip(rstripped_line[-1])
                    .replace("DatasetInfo(", "")
                    .replace("'", "")
                    .replace("(Frenchpart)", "")
                    .replace("(Dutchpart)", "")
                    .replace("(Malvinas)", "")
                )

                post_processed_line = split(
                    r",(?![^(]*\))", preprocessed_line
                )  # Used regex to exclude commas inside parentheses.

                for idx, i in enumerate(post_processed_line):
                    post_processed_line[idx] = i.replace("({", "{").replace("})", "}")

                tmp_d = dict()
                for pair in post_processed_line:
                    try:
                        pair = pair.replace(
                            "'butisdevidedintoonefilepercountry(ISO3166-1definition).EachfilecontainsLatitudeandLongitudecoordinatesdescribingthegeographicalgrid.Event-IDandfurthermetadatadescribingeacheventandamatrixreportingthemaximumwindgustspeedinMetersperSecond[m/s]pereventandgridcoordinate.ThePython3.6scripttoreproducethisdataisavailableathttps://github.com/CLIMADA-project/climada_papers.'",
                            "",
                        )
                        splitted_pair = pair.split("=", 1)
                        tmp_d[splitted_pair[0]] = splitted_pair[1]
                    except Exception as e:
                        pass  # This does not affect the final result.

                # ****** Handle data_type field. ******
                data_type_d = dict()
                processed_data_type = (
                    tmp_d["data_type"].replace("DataTypeShortInfo(", "").replace(")", "")
                )
                for item in processed_data_type.split(","):
                    try:
                        data_type_d[item.split("=")[0]] = item.split("=")[1]
                    except Exception as e:
                        # print(e)
                        pass

                # ****** Handle files field. ******
                processed_files = tmp_d["files"].replace(")]", "").replace("[FileInfo(", "")

                files_d = dict()

                flag = True
                for item in processed_files.split(","):
                    try:
                        files_d[item.split("=")[0]] = item.split("=")[1]
                    except:
                        files = []
                        flag = False

                if flag == True:
                    files = [
                        FileInfo(
                            uuid=files_d["uuid"],
                            url=files_d["url"],
                            file_name=files_d["file_name"],
                            file_format=files_d["file_format"],
                            file_size=files_d["file_size"],
                            check_sum=files_d["check_sum"],
                        )
                    ]

                try:
                    jsonise_properties = (
                        tmp_d["properties"]
                        .replace("{", '{"')
                        .replace("}", '"}')
                        .replace(":", '":"')
                        .replace(",", '","')
                        .replace('""', '"')
                    )
                    properties_jsonised = loads(jsonise_properties)
                except Exception as e:
                    jsonise_properties = (
                        jsonise_properties.replace('"FederatedStatesof",', "")
                        .replace('"IslamicRepublicof",', "")
                        .replace('"Republicof",', "")
                        .replace('"DemocraticPeoplesRepublicof",', "")
                        .replace('"ProvinceofChina",', "")
                        .replace('"TheDemocraticRepublicofthe",', "")
                        .replace('"UnitedRepublicof",', "")
                        .replace('"BolivarianRepublicof",', "")
                        .replace('"British",', "")
                        .replace('"U.S.",', "")
                        .replace('"PlurinationalStateof",', "")
                        .replace('"AscensionandTristandaCunha",', "")
                        .replace('"Stateof",', "")
                    )
                    properties_jsonised = loads(jsonise_properties)

                if dataset_infos_filename.split("\\")[-1] == "dataset_infos_tc.txt":
                    tc.append(
                        get_list_of_datasetInfo_objects(
                            tmp_d, data_type_d, properties_jsonised, files
                        )
                    )

                elif dataset_infos_filename.split("\\")[-1] == "dataset_infos_se.txt":
                    se.append(
                        get_list_of_datasetInfo_objects(
                            tmp_d, data_type_d, properties_jsonised, files
                        )
                    )

                elif dataset_infos_filename.split("\\")[-1] == "dataset_infos_rf.txt":
                    rf.append(
                        get_list_of_datasetInfo_objects(
                            tmp_d, data_type_d, properties_jsonised, files
                        )
                    )

                else:
                    rc.append(
                        get_list_of_datasetInfo_objects(
                            tmp_d, data_type_d, properties_jsonised, files
                        )
                    )
        file.close()

    hazard_list_dataset_infos = dict()
    hazard_list_dataset_infos = {
        "tropical_cyclone": tc,
        "storm_europe": se,
        "river_flood": rf,
        "relative_cropyield": rc,
    }
    return hazard_list_dataset_infos


def get_valid_hazards(hazard_list_dataset_infos: dict, exposures: list) -> dict:
    """
    A method to help populate the climate scenario drop down list in the Climada UI based
    on the selected exposure/s and hazard.

    Parameters
    ----------
    hazard_list_dataset_infos : list, required
        A list holding the full path filenames where the 4 fetched list_dataset infos are stored inside the project directory optionally.
    exposures : list, required
        A list of strings holding the selected exposure/s.

    Returns
    -------
    response
        A dictionary object containing the data and the status.
    """
    hazards_for_exposures = [
        [] for _ in exposures
    ]  # Create list of empty lists based on number of given (selected) exposures.
    try:
        client = Client()
        for idx, exposure in enumerate(exposures):
            try:
                if isinstance(
                    client.get_property_values(
                        hazard_list_dataset_infos["tropical_cyclone"],
                        known_property_values={"country_name": exposure},
                    ),
                    dict,
                ):
                    hazards_for_exposures[idx].append("tropical_cyclone")

            except:
                pass

            try:
                if isinstance(
                    client.get_property_values(
                        hazard_list_dataset_infos["river_flood"],
                        known_property_values={"country_name": exposure},
                    ),
                    dict,
                ):
                    hazards_for_exposures[idx].append("river_flood")
            except:
                pass

            try:
                if isinstance(
                    client.get_property_values(
                        hazard_list_dataset_infos["storm_europe"],
                        known_property_values={"country_name": exposure},
                    ),
                    dict,
                ):
                    hazards_for_exposures[idx].append("storm_europe")
            except:
                pass

        hazards = hazards_for_exposures[0]
        for idx, hazard_for_exposures in enumerate(hazards_for_exposures):
            hazards = list(set(hazards) & set(hazard_for_exposures))

        if len(hazards) == 0:
            hazards = dict()
            status = {
                "code": 3000,
                "message": "No hazards found for Exposures provided.",
            }

        else:
            status = {
                "code": 2000,
                "message": "Hazard params set successfully.",
            }

        data = {"exposures": exposures, "hazards": hazards}

    except Exception as exception:
        status_message = str(exception)
        data = dict()
        status = {"code": 3000, "message": status_message}

    response = {
        "data": data,
        "status": status,
    }

    return response


def get_valid_scenarios(hazard_list_dataset_infos: list, exposures: list, hazard: str) -> dict:
    """
    A method to help populate the climate scenario drop down list in the Climada UI
    based on the selected exposure/s and hazard.

    Parameters
    ----------
    dataset_infos_filenames : list, required
        A list holding the full path filenames where the 4 fetched list_dataset infos are stored inside the project directory optionally.
    exposures : list, required
        A list of strings holding the selected exposure/s.
    hazard : str, required
        The selected hazard.

    Returns
    -------
    response
        A dictionary object containing the data and the status.
    """

    try:
        client = Client()
        valid_scenarios = []
        for country in exposures:
            # Right now all storm_europe datasets contain only historical data, so no rcp
            # scenarios are available.
            if hazard == "storm_europe":
                if not "historical" in valid_scenarios:
                    valid_scenarios.append("historical")

            else:
                # In case relative_cropyield is added to the hazards list, this needs to be changed,
                # as relative cropyield does not contain country_name in known_property_values prop.
                _scenarios = client.get_property_values(
                    hazard_list_dataset_infos[hazard],
                    known_property_values={"country_name": country},
                )["climate_scenario"]
                for scenario in _scenarios:
                    if scenario not in valid_scenarios:
                        valid_scenarios.append(scenario)

    except Exception as exception:
        data = {"scenarios": [], "horizon": []}
        status = {"code": 3000, "message": f"Exception occured: {str(exception)}"}

    data = {"scenarios": valid_scenarios, "horizon": []}
    status = {
        "code": 2000,
        "message": "Climate scenario params set successfully.",
    }
    response = {"data": data, "status": status}

    return response


def get_valid_horizons(
    hazard_list_dataset_infos: list, exposures: list, hazard: str, scenario: str
) -> dict:
    """
    A method to help populate the time horizon slide bar in the Climada UI based
    on the selected exposure/s, hazard and climate scenario.

    Parameters
    ----------
    hazard_list_dataset_infos : list, required
        A list holding the full path filenames where the 4 fetched list_dataset infos are stored inside the project directory optionally.
    exposures : list, required
        A list of strings holding the selected exposure/s.
    hazard : str, required
        The selected hazard.
    scenario : str, required
        The selected scenario.

    Returns
    -------
    response
        A dictionary object containing the data and the status.
    """
    try:
        client = Client()
        horizons_for_exposures_hazard_scenario = [
            [] for item in exposures
        ]  # Create list of empty lists based on number of exposures.
        for idx, xpsr in enumerate(exposures):
            if hazard == "river_flood":
                horizons_for_exposures_hazard_scenario[idx] = client.get_property_values(
                    hazard_list_dataset_infos[hazard],
                    known_property_values={
                        "country_name": exposures[idx],
                        "climate_scenario": scenario,
                    },
                )["year_range"]
            if hazard == "storm_europe":
                horizons_for_exposures_hazard_scenario[idx] = client.get_property_values(
                    hazard_list_dataset_infos[hazard],
                    known_property_values={
                        "country_name": exposures[idx],
                    },
                )["year_range"]

            # The list_dataset_infos data for the tropical_cyclone hazard do not contain a year_range property.
            elif hazard == "tropical_cyclone":
                if scenario == "historical":
                    horizons_for_exposures_hazard_scenario[idx] = client.get_property_values(
                        hazard_list_dataset_infos[hazard],
                        known_property_values={
                            "country_name": exposures[idx],
                            "climate_scenario": scenario,
                        },
                    )["tracks_year_range"]

                else:
                    horizons_for_exposures_hazard_scenario[idx] = client.get_property_values(
                        hazard_list_dataset_infos[hazard],
                        known_property_values={
                            "country_name": exposures[idx],
                            "climate_scenario": scenario,
                        },
                    )["ref_year"]
            else:
                pass

        data = horizons_for_exposures_hazard_scenario[0]

        for idx, horizon_for_exposures_hazard_scenario in enumerate(
            horizons_for_exposures_hazard_scenario
        ):
            data = list(set(data) & set(horizon_for_exposures_hazard_scenario))

        if len(data) == 0:
            status = {
                "code": 3000,
                "message": "No time horizons found for Exposures, hazard and climate scenario provided.",
            }

        else:
            status = {"code": 2000, "message": "Time horizon params set successfully"}

    except Exception as exception:
        data = []
        status = {
            "code": 3000,
            "message": f"Exception occured while trying to get Time horizon. More info: {exception}",
        }

    response = {
        "data": data,
        "status": status,
    }

    return response


# Methods from xlsx


def get_aggregated_exposure(exposure: Exposures) -> float:
    """
    Get the aggregated exposure from a climada.entity.exposures.Exposures object.

    Parameters
    ----------
    exposure: climada.entity.exposures.Exposures, required
        Exposure object for which to calculate the aggregated exposure.

    Returns
    -------
    exposure_aggregated: float
    """
    exposure_aggregated = exposure.gdf["value"].sum()

    return exposure_aggregated


def get_exposure_per_country(exposure: Exposures) -> pd.DataFrame:
    """
    Get the exposure per country pandas.DataFrame from a climada.entity.exposures.Exposures object.

    Parameters
    ----------
    exposure: climada.entity.exposures.Exposures, required
        Exposure object for which to calculate the aggregated exposure.

    Returns
    -------
    exposure_per_country: pandas.DataFrame
    """
    exposure_per_country = exposure.gdf
    exposure_per_country["sum_value"] = exposure_per_country.groupby(["country"])[
        "value"
    ].transform("sum")
    exposure_per_country = exposure_per_country.drop_duplicates(subset=["country"])
    exposure_per_country = exposure_per_country[["country", "sum_value"]]
    exposure_per_country = exposure_per_country.dropna()
    exposure_per_country = exposure_per_country.sort_values("country").reset_index(drop=True)
    exposure_per_country.columns = ["Country", "Total exposed value in EUR"]

    return exposure_per_country


def is_connected() -> bool:
    """
    Check if there is an active internet connection.

    Parameters
    ----------
    None

    Returns:
        bool: True if connected to the internet, False otherwise.
    """
    try:
        # Attempt to connect to a known website (google.com) with a short timeout (1 second)
        urllib.request.urlopen("http://google.com", timeout=1)
        return True  # Connection was successful
    except urllib.request.URLError:
        return False  # An error occurred, indicating no internet connection
