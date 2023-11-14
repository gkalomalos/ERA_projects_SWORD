from climada.util.api_client import Client

import geopandas as gpd
import logging
import pandas as pd
from pathlib import Path

from constants import DATA_EXPOSURES_DIR, FEATHERS_DIR, SHAPEFILES_DIR
import handlers

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# Create a console handler and set its level to INFO
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Add the console handler to the logger
logger.addHandler(console_handler)


def generate_countries_gdf(eurostat_shp: gpd.GeoDataFrame = None) -> gpd.GeoDataFrame:
    """
    Generate a geopandas GeoDataFrame that contains information about each European country, including population
    density information.

    Parameters
    
    eurostat_shp: gpd.GeoDataFrame, optional
        A GeoDataFrame of the NUTS regions in the European Union. If None, reads the data from file.

    Returns

    A GeoDataFrame with the following columns:
    - NUTS_ID: the unique identifier of each administrative region.
    - LEVL_CODE: the level of administrative division.
    - CNTR_CODE: the country code according to ISO 3166-1 alpha-2.
    - NAME_LATN: the name of the administrative region in the latin alphabet.
    - NUTS_NAME: the name of the administrative region in the local language.
    - MOUNT_TYPE: the type of region (mountain or not).
    - URBN_TYPE: the type of region (urban or not).
    - COAST_TYPE: the type of region (coastal or not).
    - FID: the unique identifier of each region in the original dataset.
    - geometry: the geographic representation of the administrative region.
    - value: the exposure value for each administrative region.

    Examples

    >>> countries_gdf = generate_countries_gdf()
    >>> print(countries_gdf.head())

    NUTS_ID    LEVL_CODE   CNTR_CODE   NAME_LATN   NUTS_NAME   MOUNT_TYPE  URBN_TYPE   COAST_TYPE  FID     geometry    value
    AT      AT    AT   AUT    Österreich  Österreich  Non-mountain    Non-urban   Coastal     AT  MULTIPOLYGON ...  51288.109201
    BE1     BE    BE   BEL    Région de Bruxelles-Capitale      Bruxelles-Capitale  Non-mountain    Urban   Non-coastal     BE1000001   MULTIPOLYGON ...  40187.098954
    BE2     BE    BE   BEL    Prov. Antwerpen      Antwerpen   Non-mountain    Non-urban   Coastal     BE2110000   MULTIPOLYGON ...  416166.143935
    BE21    BE2   BE2  BEL    Arr. Antwerpen      Arr. Antwerpen  Non-mountain    Non-urban   Coastal     BE2111000   MULTIPOLYGON ...  245010.387023
    BE22    BE2   BE2  BEL    Arr. Mechelen      Arr. Mechelen   Non-mountain    Non-urban   Coastal     BE2112000   MULTIPOLYGON ...  112361.516233

    Notes

    This function generates a geodataframe with the information of the administrative regions of each EU country and their
    exposure values, which is obtained from the litpop exposures in Climada. First, it reads the European Environment Agency
    dataset, which is preprocessed and saved as a feather file. Then, it iterates over the countries, extracts the exposure
    values from Climada, and performs a spatial join to link them to the corresponding administrative regions. The exposure
    values are summed for each region and assigned to the corresponding country and region. Finally, the function returns a
    geodataframe with the country and region information, including the exposure values.
    """
    client = Client()
    logging.info("Generating Countries GeoDataFrame...")
    if not eurostat_shp:
        eurostat_shp = gpd.read_file(Path(SHAPEFILES_DIR, "NUTS_RG_01M_2021_4326.shp"))

    eurostat_eea_countries = eurostat_shp[eurostat_shp["LEVL_CODE"] == 0]
    eea_countries_gdf_list = []
    for country_code in eurostat_eea_countries["CNTR_CODE"].unique():
        country_iso3alpha = handlers.convert_iso2_to_iso3(country_code)
        exp_gdf = client.get_exposures(
            exposures_type="litpop",
            properties={"country_iso3alpha": country_iso3alpha, "exponents": "(1,1)"},
            dump_dir=Path(DATA_EXPOSURES_DIR),
        ).gdf

        country_gdf = eurostat_eea_countries[
            eurostat_eea_countries["CNTR_CODE"] == country_code
        ]
        # First, perform the spatial join to get the points within the polygons
        exp_gdf_within_eea = gpd.sjoin(
            exp_gdf, country_gdf, predicate="within", how="inner"
        )

        # Next, group the points by NUTS_ID and sum the value
        grouped = (
            exp_gdf_within_eea[exp_gdf_within_eea["LEVL_CODE"] == 0]
            .groupby("NUTS_ID")["value"]
            .sum()
        )

        # Finally, create a new column 'value' in country_gdf with the summed values for each NUTS_ID
        country_gdf["value"] = country_gdf["NUTS_ID"].map(grouped)
        eea_countries_gdf_list.append(country_gdf)
    eea_countries_gdf = pd.concat(eea_countries_gdf_list, ignore_index=True)
    # Log message to indicate that the process has finished
    logging.info("Finished generating Countries GeoDataFrame.")
    eea_countries_gdf.to_feather(
        Path(FEATHERS_DIR, "COUNTRIES_EEA_RG_01M_2021.feather")
    )
    logging.info("Finished storing Countries GeoDataFrame to feather file.")

    return eea_countries_gdf


def generate_nuts1_gdf(eurostat_shp: gpd.GeoDataFrame = None):
    """
    Generates a GeoDataFrame of the NUTS1-level regions in the European Union with added population data.

    Parameters

    eurostat_shp: gpd.GeoDataFrame, optional
        A GeoDataFrame of the NUTS regions in the European Union. If None, reads the data from file.

    Returns

    A GeoDataFrame with the following columns:
    - NUTS_ID: the unique identifier of each administrative region.
    - LEVL_CODE: the level of administrative division.
    - CNTR_CODE: the country code according to ISO 3166-1 alpha-2.
    - NAME_LATN: the name of the administrative region in the latin alphabet.
    - NUTS_NAME: the name of the administrative region in the local language.
    - MOUNT_TYPE: the type of region (mountain or not).
    - URBN_TYPE: the type of region (urban or not).
    - COAST_TYPE: the type of region (coastal or not).
    - FID: the unique identifier of each region in the original dataset.
    - geometry: the geographic representation of the administrative region.
    - value: the exposure value for each administrative region.

    Examples

    >>> nuts1_gdf = generate_nuts1_gdf()
    >>> print(nuts1_gdf.head())

    NUTS_ID  LEVL_CODE CNTR_CODE            NAME_LATN            NUTS_NAME   geometry         value
    0     CY0          1        CY               Kýpros               Κύπρος   MULTIPOLYGON (((34.60609 35.70767, 34.60060 35...  7.272121e+10
    1     DEA          1        DE  Nordrhein-Westfalen  Nordrhein-Westfalen   POLYGON ((8.70301 52.50044, 8.69906 52.48690, ...  4.617790e+12
    2     DE7          1        DE               Hessen               Hessen   MULTIPOLYGON (((9.68533 51.58202, 9.69019 51.5...  1.220987e+12
    3     DE1          1        DE    Baden-Württemberg    Baden-Württemberg   MULTIPOLYGON (((10.08372 49.54356, 10.08747 49...  1.884681e+12
    4     DEF          1        DE   Schleswig-Holstein   Schleswig-Holstein   MULTIPOLYGON (((11.16531 54.52147, 11.19997 54...  3.709941e+11

    Notes

    This function generates a geodataframe with the information of the administrative regions of each EU country and their
    exposure values, which is obtained from the litpop exposures in Climada. First, it reads the European Environment Agency
    dataset, which is preprocessed and saved as a feather file. Then, it iterates over the countries, extracts the exposure
    values from Climada, and performs a spatial join to link them to the corresponding administrative regions. The exposure
    values are summed for each region and assigned to the corresponding country and region. Finally, the function returns a
    geodataframe with the country and region information, including the exposure values.
    This function requires the following files to be available in the paths defined in the config file:
    - EEA_RG_01M_2021.feather
    """
    client = Client()
    logging.info("Generating NUTS1 GeoDataFrame...")
    if not eurostat_shp:
        eurostat_shp = gpd.read_file(Path(SHAPEFILES_DIR, "NUTS_RG_01M_2021_4326.shp"))
    eurostat_eea_nuts1 = eurostat_shp[eurostat_shp["LEVL_CODE"] == 1]
    eea_nuts1_gdf_list = []
    for country_code in eurostat_eea_nuts1["CNTR_CODE"].unique():
        country_iso3alpha = handlers.convert_iso2_to_iso3(country_code)
        exp_gdf = client.get_exposures(
            exposures_type="litpop",
            properties={"country_iso3alpha": country_iso3alpha, "exponents": "(1,1)"},
            dump_dir=Path(DATA_EXPOSURES_DIR),
        ).gdf

        eurostat_country = eurostat_eea_nuts1[
            eurostat_eea_nuts1["CNTR_CODE"] == country_code
        ]
        for nuts1_code in eurostat_country["NUTS_ID"].unique():
            nuts1_gdf = eurostat_country[eurostat_country["NUTS_ID"] == nuts1_code]
            # First, perform the spatial join to get the points within the polygons
            exp_gdf_within_nuts1 = gpd.sjoin(
                exp_gdf, nuts1_gdf, predicate="within", how="inner"
            )

            # Next, group the points by NUTS_ID and sum the value
            grouped = (
                exp_gdf_within_nuts1[exp_gdf_within_nuts1["LEVL_CODE"] == 1]
                .groupby("NUTS_ID")["value"]
                .sum()
            )

            # Finally, create a new column 'value' in country_gdf with the summed values for each NUTS_ID
            nuts1_gdf["value"] = nuts1_gdf["NUTS_ID"].map(grouped)
            eea_nuts1_gdf_list.append(nuts1_gdf)
    eea_countries_gdf = pd.concat(eea_nuts1_gdf_list, ignore_index=True)

    # Log message to indicate that the process has finished
    logging.info("Finished generating NUTS1 GeoDataFrame.")
    eea_countries_gdf.to_feather(Path(FEATHERS_DIR, "NUTS1_EEA_RG_01M_2021.feather"))

    logging.info("Finished storing NUTS1 GeoDataFrame to feather file.")
    return eea_countries_gdf


def generate_nuts2_gdf(eurostat_shp: gpd.GeoDataFrame = None):
    """
    Generates a GeoDataFrame of the NUTS2-level regions in the European Union with added population data.

    Parameters

    eurostat_shp: gpd.GeoDataFrame, optional
        A GeoDataFrame of the NUTS regions in the European Union. If None, reads the data from file.

    Returns

    A GeoDataFrame with the following columns:
    - NUTS_ID: the unique identifier of each administrative region.
    - LEVL_CODE: the level of administrative division.
    - CNTR_CODE: the country code according to ISO 3166-1 alpha-2.
    - NAME_LATN: the name of the administrative region in the latin alphabet.
    - NUTS_NAME: the name of the administrative region in the local language.
    - MOUNT_TYPE: the type of region (mountain or not).
    - URBN_TYPE: the type of region (urban or not).
    - COAST_TYPE: the type of region (coastal or not).
    - FID: the unique identifier of each region in the original dataset.
    - geometry: the geographic representation of the administrative region.
    - value: the exposure value for each administrative region.

    Examples

    >>> nuts1_gdf = generate_nuts2_gdf()
    >>> print(nuts2_gdf.head())

    NUTS_ID  LEVL_CODE CNTR_CODE                   NAME_LATN   geometry         value
    0    FRB0          2        FR       Centre — Val de Loire   POLYGON ((1.50153 48.94105, 1.51118 48.93461, ...  2.677990e+11
    1    FRD1          2        FR             Basse-Normandie   MULTIPOLYGON (((-1.11959 49.32227, -1.11292 49...  1.123014e+11
    2    FR10          2        FR               Ile-de-France   POLYGON ((2.59053 49.07965, 2.60495 49.08733, ...  4.429106e+12
    3    FRL0          2        FR  Provence-Alpes-Côte d’Azur   POLYGON ((2.59053 49.07965, 2.60495 49.08733, ...  4.429106e+12
    4    FRF2          2        FR           Champagne-Ardenne   MULTIPOLYGON (((4.96943 49.80183, 4.99626 49.8...  1.545595e+11

    Notes

    This function generates a geodataframe with the information of the administrative regions of each EU country and their
    exposure values, which is obtained from the litpop exposures in Climada. First, it reads the European Environment Agency
    dataset, which is preprocessed and saved as a feather file. Then, it iterates over the countries, extracts the exposure
    values from Climada, and performs a spatial join to link them to the corresponding administrative regions. The exposure
    values are summed for each region and assigned to the corresponding country and region. Finally, the function returns a
    geodataframe with the country and region information, including the exposure values.
    This function requires the following files to be available in the paths defined in the config file:
    - EEA_RG_01M_2021.feather
    """
    client = Client()
    if not eurostat_shp:
        eurostat_shp = gpd.read_file(Path(SHAPEFILES_DIR, "NUTS_RG_01M_2021_4326.shp"))
    eurostat_eea_nuts2 = eurostat_shp[eurostat_shp["LEVL_CODE"] == 2]
    eea_nuts2_gdf_list = []
    for country_code in eurostat_eea_nuts2["CNTR_CODE"].unique():
        country_iso3alpha = handlers.convert_iso2_to_iso3(country_code)
        exp_gdf = client.get_exposures(
            exposures_type="litpop",
            properties={"country_iso3alpha": country_iso3alpha, "exponents": "(1,1)"},
            dump_dir=Path(DATA_EXPOSURES_DIR),
        ).gdf

        eurostat_country = eurostat_eea_nuts2[
            eurostat_eea_nuts2["CNTR_CODE"] == country_code
        ]
        for nuts2_code in eurostat_country["NUTS_ID"].unique():
            nuts2_gdf = eurostat_country[eurostat_country["NUTS_ID"] == nuts2_code]
            # First, perform the spatial join to get the points within the polygons
            exp_gdf_within_nuts2 = gpd.sjoin(
                exp_gdf, nuts2_gdf, predicate="within", how="inner"
            )

            # Next, group the points by NUTS_ID and sum the value
            grouped = (
                exp_gdf_within_nuts2[exp_gdf_within_nuts2["LEVL_CODE"] == 2]
                .groupby("NUTS_ID")["value"]
                .sum()
            )

            # Finally, create a new column 'value' in country_gdf with the summed values for each NUTS_ID
            nuts2_gdf["value"] = nuts2_gdf["NUTS_ID"].map(grouped)
            eea_nuts2_gdf_list.append(nuts2_gdf)
    eea_countries_gdf = pd.concat(eea_nuts2_gdf_list, ignore_index=True)

    # Log message to indicate that the process has finished
    logging.info("Finished generating NUTS2 GeoDataFrame.")
    eea_countries_gdf.to_feather(Path(FEATHERS_DIR, "NUTS2_EEA_RG_01M_2021.feather"))
    logging.info("Finished storing NUTS2 GeoDataFrame to feather file.")

    return eea_countries_gdf


def generate_nuts3_gdf(eurostat_shp: gpd.GeoDataFrame = None):
    """
    Generates a GeoDataFrame of the NUTS3-level regions in the European Union with added population data.

    Parameters

    eurostat_shp: gpd.GeoDataFrame, optional
        A GeoDataFrame of the NUTS regions in the European Union. If None, reads the data from file.

    Returns

    A GeoDataFrame with the following columns:
    - NUTS_ID: the unique identifier of each administrative region.
    - LEVL_CODE: the level of administrative division.
    - CNTR_CODE: the country code according to ISO 3166-1 alpha-2.
    - NAME_LATN: the name of the administrative region in the latin alphabet.
    - NUTS_NAME: the name of the administrative region in the local language.
    - MOUNT_TYPE: the type of region (mountain or not).
    - URBN_TYPE: the type of region (urban or not).
    - COAST_TYPE: the type of region (coastal or not).
    - FID: the unique identifier of each region in the original dataset.
    - geometry: the geographic representation of the administrative region.
    - value: the exposure value for each administrative region.

    Examples

    >>> nuts3_gdf = generate_nuts3_gdf()
    >>> print(nuts3_gdf.head())

    NUTS_ID  LEVL_CODE CNTR_CODE                   NAME_LATN   geometry         value
    0    FRB0          2        FR       Centre — Val de Loire   POLYGON ((1.50153 48.94105, 1.51118 48.93461, ...  2.677990e+11
    1    FRD1          2        FR             Basse-Normandie   MULTIPOLYGON (((-1.11959 49.32227, -1.11292 49...  1.123014e+11
    2    FR10          2        FR               Ile-de-France   POLYGON ((2.59053 49.07965, 2.60495 49.08733, ...  4.429106e+12
    3    FRL0          2        FR  Provence-Alpes-Côte d’Azur   POLYGON ((2.59053 49.07965, 2.60495 49.08733, ...  4.429106e+12
    4    FRF2          2        FR           Champagne-Ardenne   MULTIPOLYGON (((4.96943 49.80183, 4.99626 49.8...  1.545595e+11

    Notes

    This function generates a geodataframe with the information of the administrative regions of each EU country and their
    exposure values, which is obtained from the litpop exposures in Climada. First, it reads the European Environment Agency
    dataset, which is preprocessed and saved as a feather file. Then, it iterates over the countries, extracts the exposure
    values from Climada, and performs a spatial join to link them to the corresponding administrative regions. The exposure
    values are summed for each region and assigned to the corresponding country and region. Finally, the function returns a
    geodataframe with the country and region information, including the exposure values.
    This function requires the following files to be available in the paths defined in the config file:
    - EEA_RG_01M_2021.feather
    """
    client = Client()
    if not eurostat_shp:
        eurostat_shp = gpd.read_file(Path(SHAPEFILES_DIR, "NUTS_RG_01M_2021_4326.shp"))
    eurostat_eea_nuts3 = eurostat_shp[eurostat_shp["LEVL_CODE"] == 3]
    eea_nuts3_gdf_list = []
    for country_code in eurostat_eea_nuts3["CNTR_CODE"].unique():
        country_iso3alpha = handlers.convert_iso2_to_iso3(country_code)
        exp_gdf = client.get_exposures(
            exposures_type="litpop",
            properties={"country_iso3alpha": country_iso3alpha, "exponents": "(1,1)"},
            dump_dir=Path(DATA_EXPOSURES_DIR),
        ).gdf

        eurostat_country = eurostat_eea_nuts3[
            eurostat_eea_nuts3["CNTR_CODE"] == country_code
        ]
        for nuts3_code in eurostat_country["NUTS_ID"].unique():
            nuts3_gdf = eurostat_country[eurostat_country["NUTS_ID"] == nuts3_code]
            # First, perform the spatial join to get the points within the polygons
            exp_gdf_within_nuts3 = gpd.sjoin(
                exp_gdf, nuts3_gdf, predicate="within", how="inner"
            )

            # Next, group the points by NUTS_ID and sum the value
            grouped = (
                exp_gdf_within_nuts3[exp_gdf_within_nuts3["LEVL_CODE"] == 3]
                .groupby("NUTS_ID")["value"]
                .sum()
            )

            # Finally, create a new column 'value' in country_gdf with the summed values for each NUTS_ID
            nuts3_gdf["value"] = nuts3_gdf["NUTS_ID"].map(grouped)
            eea_nuts3_gdf_list.append(nuts3_gdf)
    eea_countries_gdf = pd.concat(eea_nuts3_gdf_list, ignore_index=True)

    # Log message to indicate that the process has finished
    logging.info("Finished generating NUTS3 GeoDataFrame.")
    eea_countries_gdf.to_feather(Path(FEATHERS_DIR, "NUTS3_EEA_RG_01M_2021.feather"))
    logging.info("Finished storing NUTS3 GeoDataFrame to feather file.")

    return eea_countries_gdf


def generate_eea_values_gdf():
    if not Path(FEATHERS_DIR, "EEA_RG_01M_2021_values.feather").is_file():
        if not Path(FEATHERS_DIR, "COUNTRIES_EEA_RG_01M_2021.feather").is_file():
            generate_countries_gdf()
        if not Path(FEATHERS_DIR, "NUTS1_EEA_RG_01M_2021.feather").is_file():
            generate_nuts1_gdf()
        if not Path(FEATHERS_DIR, "NUTS2_EEA_RG_01M_2021.feather"):
            generate_nuts2_gdf()
        if not Path(FEATHERS_DIR, "NUTS3_EEA_RG_01M_2021.feather").is_file():
            generate_nuts3_gdf()
        EEA_RG_01M_2021_values = pd.concat(
            [
                gpd.read_feather(
                    Path(FEATHERS_DIR, "COUNTRIES_EEA_RG_01M_2021.feather")
                ),
                gpd.read_feather(Path(FEATHERS_DIR, "NUTS1_EEA_RG_01M_2021.feather")),
                gpd.read_feather(Path(FEATHERS_DIR, "NUTS2_EEA_RG_01M_2021.feather")),
                gpd.read_feather(Path(FEATHERS_DIR, "NUTS3_EEA_RG_01M_2021.feather")),
            ]
        )
        EEA_RG_01M_2021_values = gpd.GeoDataFrame(
            EEA_RG_01M_2021_values, crs="EPSG:4326"
        )
        EEA_RG_01M_2021_values.to_feather(
            Path(FEATHERS_DIR, "EEA_RG_01M_2021_values.feather")
        )
    else:
        EEA_RG_01M_2021_values = gpd.read_feather(
            Path(FEATHERS_DIR, "EEA_RG_01M_2021_values.feather")
        )
    return EEA_RG_01M_2021_values


def list_dataset_infos(update: bool = False):
    """
    Retrieve the dataset information from the server or from a local feather file.

    Parameters

    update : bool, optional
        Whether to retrieve the dataset information from the server or from a local feather file. Defaults to False.

    Returns

    pd.DataFrame
        The dataset information as a pandas DataFrame.

    Examples

    Retrieve dataset information from a feather file:
        >>> df = list_dataset_infos(update=False)

    Update and retrieve dataset information from the server:
        >>> df = list_dataset_infos(update=True)

    Notes

    This method retrieves information about datasets from the server or from a local feather file. If the `update`
    parameter is set to False, the method reads the dataset information from a feather file located in the
    `FEATHERS_DIR` directory. If the feather file does not exist, the method sets the `update` parameter to True
    and retrieves the dataset information from the server. The dataset information is retrieved for the following
    data types: 'river_flood' and 'storm_europe'.
    """

    # Define the path to the feather file
    feather_file = Path(FEATHERS_DIR, "list_dataset_infos.feather")
    DATA_TYPES = ["river_flood", "storm_europe"]

    # If not updating, read the dataset information from the feather file
    if not update:
        logger.info("Reading dataset information from the feather file...")
        try:
            list_dataset_infos_df = pd.read_feather(feather_file)
        except FileNotFoundError:
            logger.warning(f"Feather file '{feather_file}' not found.")
            return None

    # If updating, retrieve the dataset information from the server
    else:
        # Set up the API client
        logger.info("Connecting to the server...")
        try:
            client = Client()
        except Exception as e:
            logger.error(f"Failed to connect to the server: {str(e)}")
            return None

        # Retrieve the dataset information for each data type
        dfs = []
        for data_type in DATA_TYPES:
            logger.info(f"Retrieving dataset information for '{data_type}'...")
            dataset_infos = None
            try:
                dataset_infos = client.list_dataset_infos(data_type=data_type)
            except Exception as e:
                logger.warning(f"Failed to retrieve dataset infos: {str(e)}")
                continue

            # Create a row for each dataset info
            rows = []
            for dataset_info in dataset_infos:
                properties = dataset_info.properties
                data_type = dataset_info.data_type.data_type
                data_type_group = dataset_info.data_type.data_type_group
                row = {
                    "uuid": dataset_info.uuid,
                    "data_type": data_type,
                    "data_type_group": data_type_group,
                    "name": dataset_info.name,
                    "version": dataset_info.version,
                    "status": dataset_info.status,
                    "res_arcsec": properties.get("res_arcsec"),
                    "climate_scenario": properties.get("climate_scenario")
                    if data_type == "river_flood"
                    else "historical",
                    "year_range": properties.get("year_range"),
                    "climada_version": properties.get("climada_version"),
                    "spatial_coverage": properties.get("spatial_coverage"),
                    "country_iso3alpha": properties.get("country_iso3alpha"),
                    "country_name": properties.get("country_name"),
                    "country_iso3num": properties.get("country_iso3num"),
                    "date_creation": properties.get("date_creation"),
                }
                rows.append(row)

            # Create a DataFrame for each data type and append it to the list
            df = pd.DataFrame(rows)
            dfs.append(df)

        # Concatenate the DataFrames and reset the index
        list_dataset_infos_df = pd.concat(dfs).reset_index(drop=True)

        # Save the dataset information to the feather file
        logger.info("Saving dataset information to the feather file...")
        list_dataset_infos_df.to_feather(feather_file)

    return list_dataset_infos_df
