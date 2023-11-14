from datetime import datetime
from os import makedirs, path
from pathlib import Path

import pandas as pd
import handlers
from climada.engine import Impact
from climada.entity.exposures import Exposures
from constants import DATA_REPORTS_DIR, TEMP_DIR, FEATHERS_DIR
from xlsxwriter import Workbook

## Create exposure section


def _get_aggregated_exposure(exposure: Exposures) -> float:
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


def _get_exposure_per_country(exposure: Exposures) -> pd.DataFrame:
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
    exposure_per_country = exposure_per_country.sort_values("country").reset_index(
        drop=True
    )
    exposure_per_country.columns = ["Country", "Total exposed value in EUR"]

    return exposure_per_country


def _get_exposure_per_nuts2(exposure: Exposures) -> pd.DataFrame:
    """
    Get the exposure per nuts2 pandas.DataFrame from a climada.entity.exposures.Exposures object.

    Parameters
    ----------
    exposure: climada.entity.exposures.Exposures, required
        Exposure object for which to calculate the aggregated exposure.

    Returns
    -------
    exposure_per_nuts2: pandas.DataFrame
    """
    exposure_per_nuts2 = exposure.gdf
    exposure_per_nuts2["sum_value"] = exposure_per_nuts2.groupby(["nuts2"])[
        "value"
    ].transform("sum")
    exposure_per_nuts2 = exposure_per_nuts2.drop_duplicates(subset=["nuts2"])
    exposure_per_nuts2 = exposure_per_nuts2[
        ["country", "nuts2", "nuts_description", "sum_value"]
    ]
    exposure_per_nuts2 = exposure_per_nuts2.dropna()
    exposure_per_nuts2 = exposure_per_nuts2.sort_values(
        ["country", "nuts2"]
    ).reset_index(drop=True)
    exposure_per_nuts2.columns = [
        "Country",
        "Code 2021",
        "NUTS level 2",
        "Total exposed value in EUR",
    ]

    return exposure_per_nuts2


## Create base and expected results table section


def _get_aggregated_results_in_euro_table(
    impact_output: pd.DataFrame, hazard_type: str, baseline: bool = True
) -> pd.DataFrame:
    """
    Get the aggregated results to fill the aggregated_results_in_euro_table in the report.

    Parameters
    ----------
    impact_output: pd.DataFrame, required
        Impact output data containing all the impact data needed to generate the reports
    hazard_type: str, required
        Hazard type to search datasets.
        Example: river_flood, tropical_cyclone, storm_europe.
    baseline: bool, optional
        True to calculate baseline or False to calculate future projection.

    Returns
    -------
    all_aggregated_metrics: pandas.DataFrame
    """
    all_aggregated_metrics = {
        "RP": [],
        "sum_loss": [],
        "peril": [],
        "country": [],
    }
    hazard_type_beautified = handlers.beautify_hazard_type(hazard_type)
    all_aggregated_metrics = pd.DataFrame(all_aggregated_metrics)
    countries = list(impact_output["country"].unique())

    try:
        # Calculate the sum of losses for each event
        # impact_output['sum_loss'] = impact_output['loss'].apply(lambda loss: np.sum(loss))
        impact_output["sum_loss"] = impact_output.groupby(["event_id"])[
            "loss"
        ].transform("sum")
        impact_output = impact_output.drop_duplicates("event_id")

        # Sort sum of losses for each event from higher to lower
        impact_output = impact_output.sort_values(
            "sum_loss", ascending=False
        ).reset_index(drop=True)

        # Calculate aal
        impact_output["annual_rate_x_sum_loss"] = (
            impact_output["annual_rate"] * impact_output["sum_loss"]
        )
        aal = impact_output["annual_rate_x_sum_loss"].sum()
        all_aggregated_metrics.loc[0] = [
            "AAL",
            aal,
            hazard_type_beautified,
            ", ".join(countries),
        ]

        # Calculate rpl
        impact_output["exceedance_probability"] = impact_output["annual_rate"].cumsum()
        impact_output["RP"] = 1 / impact_output["exceedance_probability"]

        # Write data to temp directory to be used in pdf generation
        if baseline:
            impact_output.to_feather(
                path.join(TEMP_DIR, "impact_output_aggregated_baseline.feather")
            )
        else:
            impact_output.to_feather(
                path.join(TEMP_DIR, "impact_output_aggregated_future.feather")
            )

        # Calculate rpl values
        interpolated_values = handlers.get_interp1d_value(
            impact_output[["RP", "sum_loss"]]
        )
        interpolated_values["RP"] = interpolated_values["RP"].apply(
            lambda rp: f"RPL {str(rp)}"
        )
        interpolated_values["peril"] = hazard_type_beautified
        interpolated_values["country"] = ", ".join(countries)

        # Concat aal and rpl values
        all_aggregated_metrics = pd.concat(
            [all_aggregated_metrics, interpolated_values], ignore_index=True
        )

        # Keep specific columns
        all_aggregated_metrics = all_aggregated_metrics[
            ["peril", "country", "RP", "sum_loss"]
        ]
        all_aggregated_metrics.columns = ["Peril", "Country", "Metric", "Value"]

    except Exception as exc:
        # print(
        #     f"Error while generating aggregated_results_in_euro_table. More info: {exc}"
        # )
        pass

    return all_aggregated_metrics


def _get_expected_aggregated_results_in_euro_table(
    impact_output_present: pd.DataFrame,
    impact_output_future: pd.DataFrame,
    hazard_type: str,
) -> pd.DataFrame:
    """
    Get the expected results to fill the expected_results_in_euro_table in the report.

    Parameters
    ----------
    impact_output_present: pd.DataFrame, required
        Impact output data containing all the present impact data needed to generate the reports
    impact_output_future: pd.DataFrame, required
        Impact output data containing all the future impact data needed to generate the reports
    hazard_type: str, required
        Hazard type to search datasets.
        Example: river_flood, tropical_cyclone, storm_europe.

    Returns
    -------
    all_aggregated_metrics_future: pandas.DataFrame
    """
    all_aggregated_metrics_present = _get_aggregated_results_in_euro_table(
        impact_output_present, hazard_type
    )
    all_aggregated_metrics_future = _get_aggregated_results_in_euro_table(
        impact_output_future, hazard_type, False
    )

    try:
        # Calculate value comparison with baseline
        all_aggregated_metrics_future["PValue"] = all_aggregated_metrics_present[
            "Value"
        ]
        all_aggregated_metrics_future[
            r"% change compare to baseline"
        ] = all_aggregated_metrics_future.apply(
            lambda row: handlers.compare_values(row.PValue, row.Value), axis=1
        )
        # all_aggregated_metrics_future["Value"] = all_aggregated_metrics_future[
        #     "Value"
        # ].apply(lambda value: "N/A" if value == 0 else value)
        all_aggregated_metrics_future.drop("PValue", axis=1, inplace=True)

    except Exception as exc:
        # print(
        #     f"Error while generating expected_aggregated_results_in_euro_table. More info: {exc}"
        # )
        pass

    return all_aggregated_metrics_future


def _get_country_results_in_euro_table(
    impact_output: pd.DataFrame, hazard_type: str
) -> pd.DataFrame:
    """
    Get the country results to fill the country_results_in_euro_table in the report.

    Parameters
    ----------
    impact_output: pd.DataFrame, required
        Impact output data containing all the impact data needed to generate the reports
    hazard_type: str, required
        Hazard type to search datasets.
        Example: river_flood, tropical_cyclone, storm_europe.

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
        "peril": [],
        "country": [],
    }
    hazard_type_beautified = handlers.beautify_hazard_type(hazard_type)
    all_country_metrics = pd.DataFrame(all_country_metrics)
    try:
        for country_group in calculate_country_rpl_list:
            country = country_group["country"].iloc[0]

            # Calculate the sum of losses for each event
            country_group["sum_loss"] = country_group.groupby(["event_id"])[
                "loss"
            ].transform("sum")
            country_group = country_group.drop_duplicates("event_id")

            # Sort sum of losses for each event from higher to lower
            country_group = country_group.sort_values(
                "sum_loss", ascending=False
            ).reset_index(drop=True)

            # Calculate aal
            country_group["annual_rate_x_sum_loss"] = (
                country_group["annual_rate"] * country_group["sum_loss"]
            )
            aal = country_group["annual_rate_x_sum_loss"].sum()
            all_country_metrics.loc[len(all_country_metrics)] = [
                "AAL",
                aal,
                hazard_type_beautified,
                country,
            ]

            # Calculate rpl
            country_group["exceedance_probability"] = country_group[
                "annual_rate"
            ].cumsum()
            country_group["RP"] = 1 / country_group["exceedance_probability"]

            # Calculate rpl values
            interpolated_values = handlers.get_interp1d_value(
                country_group[["RP", "sum_loss"]]
            )
            interpolated_values["RP"] = interpolated_values["RP"].apply(
                lambda rp: f"RPL {str(rp)}"
            )
            interpolated_values["peril"] = hazard_type_beautified
            interpolated_values["country"] = country

            all_country_metrics = pd.concat(
                [all_country_metrics, interpolated_values], ignore_index=True
            )

        all_country_metrics = all_country_metrics[
            ["peril", "country", "RP", "sum_loss"]
        ]
        all_country_metrics.columns = ["Peril", "Country", "Metric", "Value"]

    except Exception as exc:
        # print(f"Error while generating country_results_in_euro_table. More info: {exc}")
        pass
    return all_country_metrics


def _get_expected_country_results_in_euro_table(
    impact_output_present: pd.DataFrame,
    impact_output_future: pd.DataFrame,
    hazard_type: str,
) -> pd.DataFrame:
    """
    Get the expected country results to fill the expected_country_results_in_euro_table in the report.

    Parameters
    ----------
    impact_output_present: pd.DataFrame, required
        Impact output data containing all the present impact data needed to generate the reports
    impact_output_future: pd.DataFrame, required
        Impact output data containing all the future impact data needed to generate the reports
    hazard_type: str, required
        Hazard type to search datasets.
        Example: river_flood, tropical_cyclone, storm_europe.

    Returns
    -------
    all_country_metrics_future: pandas.DataFrame
    """
    all_country_metrics_present = _get_country_results_in_euro_table(
        impact_output_present, hazard_type
    )
    all_country_metrics_future = _get_country_results_in_euro_table(
        impact_output_future, hazard_type
    )

    try:
        all_country_metrics_future["PValue"] = all_country_metrics_present["Value"]
        all_country_metrics_future[
            r"% change compare to baseline"
        ] = all_country_metrics_future.apply(
            lambda row: handlers.compare_values(row.PValue, row.Value), axis=1
        )
        # all_country_metrics_future["Value"] = all_country_metrics_future["Value"].apply(
        #     lambda value: "N/A" if value == 0 else value
        # )
        all_country_metrics_future.drop("PValue", axis=1, inplace=True)
    except Exception as exc:
        # print(
        #     f"Error while generating expected_country_results_in_euro_table. More info: {exc}"
        # )
        pass
    return all_country_metrics_future


def _get_nuts2_results_in_euro_table(
    impact_output: pd.DataFrame, hazard_type: str
) -> pd.DataFrame:
    """
    Get the nuts2 results to fill the nuts2_results_in_euro_table in the report.

    Parameters
    ----------
    impact_output: pd.DataFrame, required
        Impact output data containing all the impact data needed to generate the reports
    hazard_type: str, required
        Hazard type to search datasets.
        Example: river_flood, tropical_cyclone, storm_europe.

    Returns
    -------
    all_nuts_metrics: pandas.DataFrame
    """

    group_by_nuts2 = impact_output.groupby(["nuts2"])
    calculate_nuts2_rpl_list = [
        group_by_nuts2.get_group(nuts2) for nuts2 in group_by_nuts2.groups
    ]

    all_nuts_metrics = {
        "RP": [],
        "sum_loss": [],
        "peril": [],
        "country": [],
        "nuts2": [],
        "nuts_description": [],
    }
    hazard_type_beautified = handlers.beautify_hazard_type(hazard_type)
    all_nuts_metrics = pd.DataFrame(all_nuts_metrics)

    try:
        for nuts2_group in calculate_nuts2_rpl_list:
            nut = nuts2_group["nuts2"].iloc[0]
            nut_description = nuts2_group["nuts_description"].iloc[0]
            country = nuts2_group["country"].iloc[0]

            # Calculate the sum of losses for each event
            nuts2_group["sum_loss"] = nuts2_group.groupby(["event_id"])[
                "loss"
            ].transform("sum")
            nuts2_group = nuts2_group.drop_duplicates("event_id")

            # Sort sum of losses for each event from higher to lower
            nuts2_group = nuts2_group.sort_values(
                "sum_loss", ascending=False
            ).reset_index(drop=True)

            # Calculate aal
            nuts2_group["annual_rate_x_sum_loss"] = (
                nuts2_group["annual_rate"] * nuts2_group["sum_loss"]
            )
            aal = nuts2_group["annual_rate_x_sum_loss"].sum()
            all_nuts_metrics.loc[len(all_nuts_metrics)] = [
                "AAL",
                aal,
                hazard_type_beautified,
                country,
                nut,
                nut_description,
            ]

            # Calculate rpl
            nuts2_group["exceedance_probability"] = nuts2_group["annual_rate"].cumsum()
            nuts2_group["RP"] = 1 / nuts2_group["exceedance_probability"]

            # Calculate rpl values
            interpolated_values = handlers.get_interp1d_value(
                nuts2_group[["RP", "sum_loss"]]
            )
            interpolated_values["RP"] = interpolated_values["RP"].apply(
                lambda rp: f"RPL {str(rp)}"
            )
            interpolated_values["peril"] = hazard_type_beautified
            interpolated_values["country"] = country
            interpolated_values["nuts2"] = nut
            interpolated_values["nuts_description"] = nut_description

            all_nuts_metrics = pd.concat(
                [all_nuts_metrics, interpolated_values], ignore_index=True
            )

        all_nuts_metrics = all_nuts_metrics[
            ["peril", "country", "nuts2", "nuts_description", "RP", "sum_loss"]
        ]
        all_nuts_metrics.columns = [
            "Peril",
            "Country",
            "Code 2021",
            "NUTS level 2",
            "Metric",
            "Value",
        ]

    except Exception as exc:
        # print(f"Error while generating nuts2_results_in_euro_table. More info: {exc}")
        pass
    return all_nuts_metrics


def _get_expected_nuts2_results_in_euro_table(
    impact_output_present: pd.DataFrame,
    impact_output_future: pd.DataFrame,
    hazard_type: str,
) -> pd.DataFrame:
    """
    Get the expected nuts2 results to fill the expected_nuts2_results_in_euro_table in the report.

    Parameters
    ----------
    impact_output_present: pd.DataFrame, required
        Impact output data containing all the present impact data needed to generate the reports
    impact_output_future: pd.DataFrame, required
        Impact output data containing all the future impact data needed to generate the reports
    hazard_type: str, required
        Hazard type to search datasets.
        Example: river_flood, tropical_cyclone, storm_europe.

    Returns
    -------
    all_nuts_metrics_future: pandas.DataFrame
    """

    all_nuts_metrics_present = _get_nuts2_results_in_euro_table(
        impact_output_present, hazard_type
    )
    all_nuts_metrics_future = _get_nuts2_results_in_euro_table(
        impact_output_future, hazard_type
    )

    try:
        all_nuts_metrics_future["PValue"] = all_nuts_metrics_present["Value"]
        all_nuts_metrics_future[
            r"% change compare to baseline"
        ] = all_nuts_metrics_future.apply(
            lambda row: handlers.compare_values(row.PValue, row.Value), axis=1
        )
        # all_nuts_metrics_future["Value"] = all_nuts_metrics_future["Value"].apply(
        #     lambda value: "N/A" if value == 0 else value
        # )
        all_nuts_metrics_future.drop("PValue", axis=1, inplace=True)

    except Exception as exc:
        # print(
        #     f"Error while generating expected_nuts2_results_in_euro_table. More info: {exc}"
        # )
        pass
    return all_nuts_metrics_future


## Create xlsx worksheets section


def create_aggregated_results_worksheet(workbook: Workbook, data: dict):
    """
    Generate the aggregated results worksheet.

    Parameters
    ----------
    workbook: Workbook, required
        The current Workbook where the Country results worksheet will be added.
    data :
        Dictionary containing all the necessary data info:
        {
            "annual_growth": str,
            "countries": list,
            "exposure": Exposures,
            "exposure_filename": str,
            "hazard_type": str,
            "impact_function": str,
            "impact_output_data_present": pd.DataFrame,
            "impact_output_data_future": pd.DataFrame,
            "scenario": str,
            "time_horizon": str,
            "title": str,
        }

    Returns
    -------

    """
    # Extract data from data dictionary
    countries = data["countries"]
    scenario = data["scenario"]
    time_horizon = data["time_horizon"]
    annual_growth = data["annual_growth"]
    impact_output_data_present = data["impact_output_data_present"]
    impact_output_data_future = data["impact_output_data_future"]
    hazard_type_beautified = data["hazard_type"]
    exposure = data["exposure"]

    # Add new worksheet
    worksheet = workbook.add_worksheet("Aggregated results")

    # Define format variables
    bold_format = workbook.add_format({"bold": True})
    currency_format = workbook.add_format({"num_format": "#,##0.00€", "align": "right"})
    default_format = workbook.add_format({"font_color": "black"})
    percent_format = workbook.add_format({"num_format": "0%", "align": "right"})
    title_format = workbook.add_format({"bold": 1, "border": 1, "size": 16})
    wrap_format = workbook.add_format({"text_wrap": 1})

    # Merge cells and add title
    title = "Aggregated results"
    worksheet.merge_range("A1:E1", title, title_format)
    worksheet.set_row(0, 25)

    ## Create exposure section
    worksheet.write(1, 0, "1. Exposure", bold_format)
    exposure_data = _get_aggregated_exposure(exposure)

    exposure_table = [[", ".join(countries), exposure_data]]

    exposure_table_columns = [
        {"header": "Countries"},
        {"header": "Total exposed value in EUR", "format": currency_format},
    ]
    exposure_table_options = {
        "data": exposure_table,
        "columns": exposure_table_columns,
        "style": "Table Style Light 13",
        "name": "aggregated_exposure",
    }
    worksheet.add_table(f"A3:B4", options=exposure_table_options)

    # Create current results in EUR section
    worksheet.write(5, 0, "2. Current results in EUR", bold_format)

    results_data = _get_aggregated_results_in_euro_table(
        impact_output_data_present, hazard_type_beautified
    )

    # Save results to temp folder to be used in pdf report generation
    results_data.to_excel(path.join(TEMP_DIR, "aggregated_results_rpl.xlsx"))
    # The xlsxwriter .add_table() method, expects a list of lists.
    current_results_table = results_data.values.tolist()

    current_results_table_columns = [
        {"header": "Peril"},
        {"header": "Countries"},
        {"header": "Metric"},
        {"header": "Value", "format": currency_format},
    ]
    current_results_table_options = {
        "data": current_results_table,
        "columns": current_results_table_columns,
        "style": "Table Style Light 13",
        "name": "aggregated_results",
    }
    worksheet.add_table(f"A7:D18", options=current_results_table_options)

    # Create expected results in EUR section

    if scenario != "historical":
        expected_results_title = "3. Expected results in EUR"
        worksheet.write(19, 0, expected_results_title, bold_format)
        expected_results_data = _get_expected_aggregated_results_in_euro_table(
            impact_output_data_present,
            impact_output_data_future,
            hazard_type_beautified,
        )

        # Save results to temp folder to be used in pdf report generation
        expected_results_data.to_excel(
            path.join(TEMP_DIR, "expected_aggregated_results_rpl.xlsx")
        )
        # The xlsxwriter .add_table() method, expects a list of lists.
        expected_results_table = expected_results_data.values.tolist()

        expected_results_table_columns = [
            {"header": "Peril"},
            {"header": "Countries"},
            {"header": "Metric"},
            {"header": "Value", "format": currency_format},
            {"header": r"% change compare to baseline", "format": percent_format},
        ]

        expected_results_table_options = {
            "data": expected_results_table,
            "columns": expected_results_table_columns,
            "style": "Table Style Light 13",
            "name": "aggregated_expected_results",
        }

        worksheet.add_table(f"A23:E34", options=expected_results_table_options)

    # Create time horizon and rcp table
    horizon_rcp_growth_table_data = [
        ["Time horizon:", time_horizon],
        ["RCP:", scenario],
        ["Expected exposed value given the economic growth:", annual_growth],
    ]
    horizon_rcp_growth_options = {
        "data": horizon_rcp_growth_table_data,
        "style": "Table Style Light 13",
        "header_row": False,
    }
    worksheet.add_table(f"C20:D22", options=horizon_rcp_growth_options)

    # Define column width
    worksheet.set_column("A:E", 25)
    worksheet.set_column("B:C", 45)

    # Hide gridlines for presentation and printing
    worksheet.hide_gridlines(2)


def create_general_information_worksheet(workbook: Workbook, data: dict):
    """
    Generate the General information worksheet.

    Parameters
    ----------
    workbook: Workbook, required
        The current Workbook where the Country results worksheet will be added.
    data :
        Dictionary containing all the necessary data info:
        {
            "annual_growth": str,
            "countries": list,
            "exposure": Exposures,
            "exposure_filename": str,
            "hazard_type": str,
            "impact_function": str,
            "impact_output_data_present": pd.DataFrame,
            "impact_output_data_future": pd.DataFrame,
            "scenario": str,
            "time_horizon": str,
            "title": str,
        }

    Returns
    -------

    """
    # Extract data from data dictionary
    countries = data["countries"]
    impact_function = data["impact_function"]
    scenario = data["scenario"]
    time_horizon = data["time_horizon"]
    annual_growth = data["annual_growth"]
    exposure_filename = data["exposure_filename"]
    exposure_value = exposure_filename if exposure_filename else "LitPop"

    # Add new worksheet
    worksheet = workbook.add_worksheet("General information")

    # Define format variables
    italic_format = workbook.add_format({"italic": True})
    blue_format = workbook.add_format({"font_color": "blue"})

    # Define format variables
    italic_format = workbook.add_format({"italic": True})
    blue_format = workbook.add_format({"font_color": "blue"})

    # Run analysis timestamp
    dt = datetime.now().strftime(r"%d/%m/%y %H:%M:%S")
    countries_stringified = ", ".join(countries)

    # Set table data
    table_data = [
        ["Space analysis", countries_stringified],
        ["Exposure/Exposure filename", exposure_value],
        ["Impact function", impact_function],
        ["Run timestamp", dt],
        ["View", scenario],
        ["Time horizon", time_horizon],
        ["Exposure growth", annual_growth],
    ]

    # Configure column width to grow according to the countries list size
    worksheet.set_column("B:B", 25)
    worksheet.set_column("C:C", 15 * len(countries))

    # Configure table headers and options
    columns = [{"header": "Information"}, {"header": "Value"}]
    options = {"data": table_data, "style": "Table Style Light 13", "columns": columns}
    worksheet.add_table(f"B2:C10", options=options)

    worksheet.write(13, 1, "Disclaimer:", italic_format)
    worksheet.write(
        15,
        1,
        "The user interface has been developed by EIOPA to facilitate the use of CLIMADA which can be found at:",
        italic_format,
    )
    worksheet.write_url(
        16,
        1,
        "https://wcr.ethz.ch/research/climada.html",
        string="https://wcr.ethz.ch/research/climada.html",
        cell_format=blue_format,
    )
    worksheet.write(
        17,
        1,
        "The user interface is a free software. You can redistribute and/or modify it. The installation and use of the user interface is done at the user's discretion and risk.",
        italic_format,
    )
    worksheet.write(
        18,
        1,
        "The user agrees to be solely responsibility for any damage to the computer system, loss of data or any other damage resulting from installation or use of the software.",
        italic_format,
    )
    worksheet.write(
        19,
        1,
        "EIOPA shall not be responsible or liable for any damages arising in connection with downloading, installation, modifying or any other use of the software.",
        italic_format,
    )
    worksheet.write(
        20,
        1,
        "EIOPA shall assume no responsibility for any errors or other mistakes or inaccuracies in the software, in the results produced by the software or in the related documentation.",
        italic_format,
    )
    worksheet.write(22, 1, "License for CLIMADA:", italic_format)
    worksheet.write(
        23,
        1,
        "Copyright (C) 2017 ETH Zurich, CLIMADA contributors listed in AUTHORS. CLIMADA is free software: you can redistribute it and/or modify it under the terms of the",
        italic_format,
    )
    worksheet.write(
        24,
        1,
        "GNU General Public License Version 3, 29 June 2007 as published by the Free Software Foundation, https://www.gnu.org/licenses/gpl-3.0.html.",
        italic_format,
    )
    worksheet.write(
        25,
        1,
        "CLIMADA is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.",
        italic_format,
    )
    worksheet.write(
        26,
        1,
        "See the GNU General Public License for more details: https://www.gnu.org/licenses/gpl-3.0.html.",
        italic_format,
    )

    # Hide gridlines for presentation and printing
    worksheet.hide_gridlines(2)


def create_country_results_worksheet(workbook: Workbook, data: dict):
    """
    Generate the country results worksheet.

    Parameters
    ----------
    workbook: Workbook, required
        The current Workbook where the Country results worksheet will be added.
    data :
        Dictionary containing all the necessary data info:
        {
            "annual_growth": str,
            "countries": list,
            "exposure": Exposures,
            "exposure_filename": str,
            "hazard_type": str,
            "impact_function": str,
            "impact_output_data_present": pd.DataFrame,
            "impact_output_data_future": pd.DataFrame,
            "scenario": str,
            "time_horizon": str,
            "title": str,
        }

    Returns
    -------

    """
    # Extract data from data dictionary
    countries = data["countries"]
    exposure = data["exposure"]
    hazard_type_beautified = data["hazard_type"]
    impact_output_data_present = data["impact_output_data_present"]
    impact_output_data_future = data["impact_output_data_future"]
    scenario = data["scenario"]
    time_horizon = data["time_horizon"]

    # Add new worksheet
    worksheet = workbook.add_worksheet("Country results")

    # Define format variables
    bold_format = workbook.add_format({"bold": True})
    currency_format = workbook.add_format({"num_format": "#,##0.00€", "align": "right"})
    default_format = workbook.add_format({"font_color": "black"})
    percent_format = workbook.add_format({"num_format": "0%", "align": "right"})
    red_format = workbook.add_format({"font_color": "red"})
    title_format = workbook.add_format({"bold": 1, "border": 1, "size": 16})
    wrap_format = workbook.add_format({"text_wrap": 1})

    # Merge cells and add title
    title = "Country results"
    worksheet.merge_range("A1:E1", title, title_format)
    worksheet.set_row(0, 25)

    # Create exposure section
    exposure_start = 2
    worksheet.write(exposure_start, 0, "1. Exposure", bold_format)

    exposure_data = _get_exposure_per_country(exposure)

    exposure_table_length = len(exposure_data)
    exposure_table = exposure_data.values.tolist()

    exposure_table_columns = [
        {"header": "Country"},
        {"header": "Total exposed value in EUR", "format": currency_format},
    ]

    exposure_table_options = {
        "data": exposure_table,
        "columns": exposure_table_columns,
        "style": "Table Style Light 13",
        "name": "country_exposure",
    }

    exposure_table_start = exposure_start + 2
    exposure_table_end = exposure_table_start + exposure_table_length
    worksheet.add_table(
        f"A{exposure_table_start}:B{exposure_table_end}", options=exposure_table_options
    )

    ## Create results in EUR section
    results_start = exposure_table_end + 1
    worksheet.write(results_start, 0, "2. Results in EUR", bold_format)

    results_data = _get_country_results_in_euro_table(
        impact_output_data_present, hazard_type_beautified
    )
    results_table_length = len(results_data)

    # The xlsxwriter .add_table() method, expects a list of lists.
    results_table = results_data.values.tolist()

    results_table_columns = [
        {"header": "Peril"},
        {"header": "Country"},
        {"header": "Metric"},
        {"header": "Value", "format": currency_format},
    ]
    results_table_options = {
        "data": results_table,
        "columns": results_table_columns,
        "style": "Table Style Light 13",
        "name": "country_results",
    }

    results_table_start = results_start + 2
    results_table_end = results_table_start + results_table_length
    worksheet.add_table(
        f"A{results_table_start}:D{results_table_end}", options=results_table_options
    )

    # Create expected results in EUR section
    expected_results_start = results_table_end + 2
    if scenario != "historical":
        expected_results_title = "3. Expected results in EUR"
        write_rich_string(
            worksheet,
            expected_results_title,
            "Expected",
            "middle",
            expected_results_start,
            0,
            default_format,
            red_format,
        )

        expected_results_data = _get_expected_country_results_in_euro_table(
            impact_output_data_present,
            impact_output_data_future,
            hazard_type_beautified,
        )
        expected_results_table_length = len(expected_results_data)

        # The xlsxwriter .add_table() method, expects a list of lists.
        expected_results_table = expected_results_data.values.tolist()

        expected_results_table_columns = [
            {"header": "Peril"},
            {"header": "Country"},
            {"header": "Metric"},
            {"header": "Value", "format": currency_format},
            {"header": r"% change compare to baseline", "format": percent_format},
        ]

        expected_results_table_options = {
            "data": expected_results_table,
            "columns": expected_results_table_columns,
            "style": "Table Style Light 13",
            "name": "country_expected_results",
        }

        expected_results_table_start = expected_results_start + 2
        expected_results_table_end = (
            expected_results_table_start + expected_results_table_length
        )
        worksheet.add_table(
            f"A{expected_results_table_start}:E{expected_results_table_end}",
            options=expected_results_table_options,
        )

    # Create time horizon and rcp table
    horizon_rcp_table_data = [
        ["Time horizon:", time_horizon],
        ["RCP:", scenario],
    ]
    horizon_rcp_options = {
        "data": horizon_rcp_table_data,
        "style": "Table Style Light 13",
        "header_row": False,
    }
    time_horizon_rcp_table_start = expected_results_start
    time_horizon_rcp_table_end = expected_results_start + 1
    worksheet.add_table(
        f"C{time_horizon_rcp_table_start}:D{time_horizon_rcp_table_end}",
        options=horizon_rcp_options,
    )

    # Define column width
    worksheet.set_column("A:E", 25)
    worksheet.set_column("B:B", 45)

    # Hide gridlines for presentation and printing
    worksheet.hide_gridlines(2)


def create_NUTS2_results_worksheet(workbook: Workbook, data: dict):
    """
    Generate the nuts2 results worksheet.

    Parameters
    ----------
    workbook : Workbook
        The current Workbook where the Country results worksheet will be added.
    data : dict
        Dictionary containing all the necessary data info:
        {
            "annual_growth": str,
            "countries": list,
            "exposure": Exposures,
            "exposure_filename": str,
            "hazard_type": str,
            "impact_function": str,
            "impact_output_data_present": pd.DataFrame,
            "impact_output_data_future": pd.DataFrame,
            "scenario": str,
            "time_horizon": str,
            "title": str,
        }

    Returns
    -------
    None
    """
    # Extract data from data dictionary
    countries = data["countries"]
    exposure = data["exposure"]
    hazard_type_beautified = data["hazard_type"]
    impact_output_data_present = data["impact_output_data_present"]
    impact_output_data_future = data["impact_output_data_future"]
    scenario = data["scenario"]
    time_horizon = data["time_horizon"]
    title = data["title"]

    # Add new worksheet
    worksheet = workbook.add_worksheet("NUTS2 results")

    # Define format variables
    bold = workbook.add_format({"bold": True})
    currency_format = workbook.add_format({"num_format": "#,##0.00€", "align": "right"})
    percent_format = workbook.add_format({"num_format": "0%", "align": "right"})
    title_format = workbook.add_format({"bold": 1, "border": 1, "size": 16})
    wrap_format = workbook.add_format({"text_wrap": 1})

    # Merge cells and add title
    worksheet.merge_range("A1:G1", title, title_format)
    worksheet.set_row(0, 25)

    ## Create exposure section
    exposure_start = 2
    worksheet.set_column("A:G", 25)
    worksheet.write(exposure_start, 0, "1. Exposure", bold)

    exposure_data = _get_exposure_per_nuts2(exposure)
    exposure_data_length = len(exposure_data)

    exposure_table = exposure_data.values.tolist()

    columns = [
        {"header": "Country"},
        {"header": "Code 2021"},
        {"header": "NUTS level 2"},
        {"header": "Total exposed value in EUR", "format": currency_format},
    ]
    options = {
        "data": exposure_table,
        "columns": columns,
        "style": "Table Style Light 13",
        "name": "exposure",
    }
    exposure_table_start = exposure_start + 2
    exposure_table_end = exposure_table_start + exposure_data_length
    worksheet.add_table(
        f"A{exposure_table_start}:D{exposure_table_end}", options=options
    )

    ## Create results section
    results_start = exposure_table_end + 1
    worksheet.write(results_start, 0, "2. Results in EUR", bold)
    results_data = _get_nuts2_results_in_euro_table(
        impact_output_data_present, hazard_type_beautified
    )
    results_data_length = len(results_data)

    # The xlsxwriter .add_table() method, expects a list of lists.
    results_table = results_data.values.tolist()

    columns = [
        {"header": "Peril"},
        {"header": "Country"},
        {"header": "Code 2021"},
        {"header": "NUTS level 2"},
        {"header": "Metric"},
        {"header": "Value", "format": currency_format},
    ]

    options = {
        "data": results_table,
        "columns": columns,
        "style": "Table Style Light 13",
        "name": "results",
    }
    results_table_start = results_start + 2
    results_table_end = results_table_start + results_data_length

    worksheet.add_table(f"A{results_table_start}:F{results_table_end}", options=options)
    ## Create expected results section

    expected_results_start = results_table_end + 2
    if scenario != "historical":
        worksheet.write(expected_results_start, 0, "3. Expected results in EUR", bold)

        expected_results_data = _get_expected_nuts2_results_in_euro_table(
            impact_output_data_present,
            impact_output_data_future,
            hazard_type_beautified,
        )
        # if expected_results_data.empty:
        expected_results_data_length = len(expected_results_data)
        # The xlsxwriter .add_table() method, expects a list of lists.
        expected_results_table = expected_results_data.values.tolist()
        columns = [
            {"header": "Peril"},
            {"header": "Country"},
            {"header": "Code 2021"},
            {"header": "NUTS level 2"},
            {"header": "Metric"},
            {"header": "Value", "format": currency_format},
            {"header": r"% change compare to baseline", "format": percent_format},
        ]
        options = {
            "data": expected_results_table,
            "columns": columns,
            "style": "Table Style Light 13",
            "name": "expected_results",
        }
        expected_results_table_start = expected_results_start + 2
        expected_results_table_end = (
            expected_results_table_start + expected_results_data_length
        )
        worksheet.add_table(
            f"A{expected_results_table_start}:G{expected_results_table_end}",
            options=options,
        )

    ## Create time horizon and rcp table
    table_data = [
        ["Time horizon:", time_horizon],
        ["RCP:", scenario],
    ]
    options = {"data": table_data, "style": "Table Style Light 13", "header_row": False}
    time_horizon_rcp_table_start = expected_results_start
    time_horizon_rcp_table_end = expected_results_start + 1

    worksheet.add_table(
        f"C{time_horizon_rcp_table_start}:D{time_horizon_rcp_table_end}",
        options=options,
    )
    # Hide gridlines for presentation and printing
    worksheet.hide_gridlines(2)


def create_NUTS_worksheet(workbook: Workbook):
    """
    Generate the nuts2 info worksheet.

    Parameters
    ----------
    workbook: Workbook, required
        The current Workbook where the Country results worksheet will be added.

    Returns
    -------

    """
    # Read the feather file into a pandas DataFrame
    NUTS_DATA = pd.read_feather(Path(FEATHERS_DIR, "NUTS_list.feather"))

    # Add new worksheet
    worksheet = workbook.add_worksheet("List of NUTS")

    # Define table options
    options = {
        "data": NUTS_DATA.values.tolist(),
        "header_row": True,
        "style": "Table Style Light 13",
        "name": "nuts",
    }

    # Add table to worksheet
    worksheet.add_table(
        0, 0, NUTS_DATA.shape[0], NUTS_DATA.shape[1] - 1, options=options
    )

    # Define column width
    worksheet.set_column("A:B", 12)
    worksheet.set_column("C:C", 55)
    worksheet.set_column("D:F", 15)

    # Hide gridlines for presentation and printing
    worksheet.hide_gridlines(2)


## Generic methods definition


def write_rich_string(
    worksheet,
    string: str,
    enriched_string: str,
    position: str,
    row: int,
    column: int,
    default_format: dict,
    rich_format: dict,
):
    """
    Helper method to write part of strings in Excel, in different format, instead
    of formatting the whole cell.

    Parameters
    ----------
    worksheet: Worksheet
        The current active worksheet.

    Returns
    -------
    """
    enriched_start_index = string.index(enriched_string)
    enriched_end_index = enriched_start_index + len(enriched_string)

    if position == "start":
        worksheet.write_rich_string(
            row,
            column,
            default_format,
            string,
            rich_format,
            string[enriched_start_index:enriched_end_index],
        )

    if position == "middle":
        worksheet.write_rich_string(
            row,
            column,
            default_format,
            string[0:enriched_start_index],
            rich_format,
            string[enriched_start_index:enriched_end_index],
            default_format,
            " " + string[enriched_end_index + 1 :],
        )

    if position == "end":
        worksheet.write_rich_string(
            row,
            column,
            default_format,
            string[0:enriched_start_index],
            rich_format,
            string[enriched_start_index:],
        )


def create_xlsx_report(
    countries: list,
    exposure: Exposures,
    exposure_filename: str,
    hazard_type: str,
    scenario: str,
    time_horizon: str,
    annual_growth: str,
    impact_present: Impact,
    impact_present_output: pd.DataFrame = None,
    impact_future_output: pd.DataFrame = None,
):
    """
    Create new xlsx report base on user input.

    Parameters
    ----------
    annual_growth: str, required
        Annual growth of the selected exposure/s.
    countries: list, required
        List of country names for which to search for datasets.
        Example: ['Greece', 'Bulgaria', 'Slovenia']
    exposure : climada.entity.exposures.Exposures, required
        Exposure object to create xlsx report.
    hazard_type: str, required
        Hazard type to create xlsx report.
        Example: river_flood, tropical_cyclone, storm_europe.
    exposure_filename: str, required
        The filepath to the exposure .hdf5 or .xlsx file.
    scenario: str, required
        Type of scenario to search datasets.
        Example: historical, rcp26, rcp45 etc.
    time_horizon: str, required
        Time horizon to search datasets.
        Example: 1980-2000, 2030-2050 etc.
    impact_present: climada.entity.Impact, required
        Impact object for which to create xlsx report.
    impact_future: climada.entity.Impact, required
        Impact object for which to create xlsx report.

    Returns
    -------
    """
    country_codes = handlers.get_alpha2_country_codes_from_countries(countries)
    country_codes_stringified = "-".join(country_codes)
    countries_stringified = ", ".join(countries)

    hazard_type = handlers.get_hazard_type_from_impact(impact_present)

    # Transform hazard and scenario data_types to user friendly strings
    hazard_type_beautified = handlers.beautify_hazard_type(hazard_type)
    scenario_beautified = handlers.beautify_scenario(scenario)

    source = "user" if exposure_filename else "litpop"
    filename = f"{hazard_type}_10synth_tracks_150arcsec_{scenario}_{country_codes_stringified}_{time_horizon}_{source}"
    xlsx_title = f"Report for {hazard_type_beautified} in {countries_stringified} for scenario {scenario_beautified} in {time_horizon}"

    impact_function = handlers.get_impact_function_from_impact(impact_present)

    # Define reports file path
    if not path.exists(DATA_REPORTS_DIR):
        makedirs(DATA_REPORTS_DIR)

    report_file_path = path.join(DATA_REPORTS_DIR, f"{filename}.xlsx")

    impact_output_data_present = impact_present_output
    if scenario == "historical":
        impact_output_data_future = None
    else:
        impact_output_data_future = impact_future_output
        # Filter out coordinates from other countries in the exposure.

    data = {
        "annual_growth": annual_growth,
        "countries": countries,
        "exposure": exposure,
        "exposure_filename": exposure_filename,
        "hazard_type": hazard_type,
        "impact_function": impact_function,
        "impact_output_data_present": impact_output_data_present,
        "impact_output_data_future": impact_output_data_future,
        "scenario": scenario,
        "time_horizon": time_horizon,
        "title": xlsx_title,
    }
    # Create a workbook and add the respective worksheets.
    workbook = Workbook(report_file_path)

    create_general_information_worksheet(workbook, data)
    create_aggregated_results_worksheet(workbook, data)
    create_country_results_worksheet(workbook, data)
    create_NUTS2_results_worksheet(workbook, data)
    create_NUTS_worksheet(workbook)

    workbook.close()
