from datetime import datetime
from os import makedirs, path, remove
from pathlib import Path

import pandas as pd
import numpy as np
from docx2pdf import convert
from docx.shared import Mm
from docxtpl import DocxTemplate, InlineImage
from pythoncom import CoInitialize
from constants import (
    DATA_REPORTS_DIR,
    TEMPLATES_PDF_FILE,
    TEMP_DIR,
    CLIENT_ASSETS_DIR,
)

from handlers import (
    get_alpha2_country_codes_from_countries,
    beautify_scenario,
    beautify_hazard_type,
)

from plots import save_map_as_image


def create_pdf_report(
    annual_growth: str,
    countries: list,
    exposure_data: dict,
    hazard_data: dict,
    impact_data: dict,
    scenario: str,
    time_horizon: str,
):
    """
    Create new pdf report base on user input.

    Parameters
    ----------
    annual_growth: str, required
        Annual growth of the selected exposure/s.
    countries: list, required
        List of country names for which to search for datasets.
        Example: ['Greece', 'Bulgaria', 'Slovenia']
    exposure_data: dict, required
        { "filename": str, "exposure_value_aggregated": exposure_value_aggregated }
    hazard_data: dict, required
        { "filename": hazard_filename, "hazard_type": hazard_type }
    impact_data: dict, required
        { "impact_function": str }
    scenario: str, required
        Type of scenario to search datasets.
        Example: historical, rcp26, rcp45 etc.
    time_horizon: str, required
        Time horizon to search datasets.
        Example: 1980-2000, 2030-2050 etc.

    Returns
    -------
    """
    EXPOSURE_HISTAGRAM_FILE = path.join(TEMP_DIR, "aggregated_stacked_exposure.jpg")
    EXCEEDANCE_FREQ_FILE_PRESENT = path.join(
        TEMP_DIR, "exceedance_freq_curve_present.jpg"
    )
    HAZARD_RP_10 = path.join(CLIENT_ASSETS_DIR, "hazard_nuts2_rp10.png")
    HAZARD_RP_100 = path.join(CLIENT_ASSETS_DIR, "hazard_nuts2_rp100.png")
    HAZARD_RP_500 = path.join(CLIENT_ASSETS_DIR, "hazard_nuts2_rp500.png")

    if scenario != "historical":
        EXCEEDANCE_FREQ_FILE_FUTURE = path.join(
            TEMP_DIR, "exceedance_freq_curve_future.jpg"
        )

    # Set parameters
    exposure_filename = exposure_data["filename"]
    exposure_value_aggregated = f'{exposure_data["exposure_value_aggregated"]:,.2f}'
    hazard_filename = hazard_data["filename"]
    hazard_type = hazard_data["hazard_type"]
    impact_function = impact_data["impact_function"]
    # Create new document
    report_template = DocxTemplate(TEMPLATES_PDF_FILE)

    # Define reports file path
    if not path.exists(DATA_REPORTS_DIR):
        makedirs(DATA_REPORTS_DIR)

    country_codes = get_alpha2_country_codes_from_countries(countries)
    country_codes_stringified = "-".join(country_codes)
    countries_stringified = ", ".join(countries)
    scenario_beautified = beautify_scenario(scenario)
    hazard_type_beautified = beautify_hazard_type(hazard_type)
    hazard_filename = f"{hazard_type}_150arcsec_{scenario}_{country_codes_stringified}_{time_horizon}.hdf5"

    source = "user" if exposure_filename else "litpop"
    filename = f"{hazard_type}_10synth_tracks_150arcsec_{scenario}_{country_codes_stringified}_{time_horizon}_{source}"
    filepath = path.join(DATA_REPORTS_DIR, f"{filename}.docx")

    # Create section 1. Input fields
    report_title = f"Report"
    report_subtitle = f"The report summarizes the results for {hazard_type_beautified} in {countries_stringified}."

    # Run analysis timestamp
    timestamp = datetime.now().strftime(r"%d/%m/%y %H:%M:%S")

    # Create section 2. Exposure
    exposure_image = InlineImage(
        report_template,
        image_descriptor=path.join(CLIENT_ASSETS_DIR, "exposure_europe_nuts2.png"),
        width=Mm(115),
        height=Mm(80),
    )

    exposure_histogram = InlineImage(
        report_template,
        image_descriptor=EXPOSURE_HISTAGRAM_FILE,
        width=Mm(115),
        height=Mm(80),
    )

    # Create section 3. Hazard
    hazard_rp_10 = InlineImage(
        report_template, image_descriptor=HAZARD_RP_10, width=Mm(115), height=Mm(80)
    )
    hazard_rp_100 = InlineImage(
        report_template, image_descriptor=HAZARD_RP_100, width=Mm(115), height=Mm(80)
    )
    hazard_rp_500 = InlineImage(
        report_template, image_descriptor=HAZARD_RP_500, width=Mm(115), height=Mm(80)
    )
    hazard_rpl_values = pd.read_excel(
        path.join(TEMP_DIR, "aggregated_results_rpl.xlsx")
    )
    hazard_rpl_values.loc[:, "Value"] = hazard_rpl_values["Value"].map("{:,.2f}".format)

    hazard_rpl_values = list(hazard_rpl_values["Value"])
    if scenario != "historical":
        hazard_expected_rpl_values = pd.read_excel(
            path.join(TEMP_DIR, "expected_aggregated_results_rpl.xlsx")
        )
        hazard_expected_rpl_values.loc[:, "Value"] = hazard_expected_rpl_values[
            "Value"
        ].map("{:,.2f}".format)
        hazard_expected_rpl_values[
            r"% change compare to baseline"
        ] = hazard_expected_rpl_values[r"% change compare to baseline"].round(
            decimals=2
        )
        hazard_expected_rpl_values[
            r"% change compare to baseline"
        ] = hazard_expected_rpl_values[r"% change compare to baseline"].apply(
            lambda row: str(row) if np.isnan(row) else f"{str(row)}%"
        )
        hazard_expected_rpl_comparison = list(
            hazard_expected_rpl_values[r"% change compare to baseline"]
        )
        hazard_expected_rpl_values = list(hazard_expected_rpl_values["Value"])

    # Create section 4. Results
    exceedance_freq_curve_present = InlineImage(
        report_template,
        image_descriptor=EXCEEDANCE_FREQ_FILE_PRESENT,
        width=Mm(130),
        height=Mm(90),
    )

    if scenario != "historical":
        exceedance_freq_curve_future = InlineImage(
            report_template,
            image_descriptor=EXCEEDANCE_FREQ_FILE_FUTURE,
            width=Mm(130),
            height=Mm(90),
        )

    context = {
        "annual_growth": f"{str(annual_growth)}%",
        "countries": countries_stringified,
        "exposure_value_aggregated": exposure_value_aggregated,
        "exceedance_freq_curve_present": exceedance_freq_curve_present,
        "exceedance_freq_curve_future": exceedance_freq_curve_future
        if scenario != "historical"
        else "",
        "exposure_type_or_filename": "LitPop"
        if not exposure_filename
        else exposure_filename,
        "exposure_histogram": exposure_histogram,
        "hazard_rp_10": hazard_rp_10,
        "hazard_rp_100": hazard_rp_100,
        "hazard_rp_500": hazard_rp_500,
        "hazard_filename": "-" if not hazard_filename else hazard_filename,
        "hazard_type": hazard_type_beautified,
        "report_subtitle": report_subtitle,
        "report_title": report_title,
        "scenario": scenario_beautified,
        "time_horizon": time_horizon,
        "timestamp": timestamp,
        "exposure_image": exposure_image,
        "impact_function": impact_function,
        "value_aal": hazard_rpl_values[0],
        "value_rpl_1000": hazard_rpl_values[1],
        "value_rpl_750": hazard_rpl_values[2],
        "value_rpl_500": hazard_rpl_values[3],
        "value_rpl_400": hazard_rpl_values[4],
        "value_rpl_250": hazard_rpl_values[5],
        "value_rpl_200": hazard_rpl_values[6],
        "value_rpl_150": hazard_rpl_values[7],
        "value_rpl_100": hazard_rpl_values[8],
        "value_rpl_50": hazard_rpl_values[9],
        "value_rpl_10": hazard_rpl_values[10],
        "expected_value_aal": hazard_expected_rpl_values[0]
        if scenario != "historical"
        else "N/A",
        "expected_value_rpl_1000": hazard_expected_rpl_values[1]
        if scenario != "historical"
        else "N/A",
        "expected_value_rpl_750": hazard_expected_rpl_values[2]
        if scenario != "historical"
        else "N/A",
        "expected_value_rpl_500": hazard_expected_rpl_values[3]
        if scenario != "historical"
        else "N/A",
        "expected_value_rpl_400": hazard_expected_rpl_values[4]
        if scenario != "historical"
        else "N/A",
        "expected_value_rpl_250": hazard_expected_rpl_values[5]
        if scenario != "historical"
        else "N/A",
        "expected_value_rpl_200": hazard_expected_rpl_values[6]
        if scenario != "historical"
        else "N/A",
        "expected_value_rpl_150": hazard_expected_rpl_values[7]
        if scenario != "historical"
        else "N/A",
        "expected_value_rpl_100": hazard_expected_rpl_values[8]
        if scenario != "historical"
        else "N/A",
        "expected_value_rpl_50": hazard_expected_rpl_values[9]
        if scenario != "historical"
        else "N/A",
        "expected_value_rpl_10": hazard_expected_rpl_values[10]
        if scenario != "historical"
        else "N/A",
        "per_aal": hazard_expected_rpl_comparison[0]
        if scenario != "historical"
        else "N/A",
        "per_rpl_1000": hazard_expected_rpl_comparison[1]
        if scenario != "historical"
        else "N/A",
        "per_rpl_750": hazard_expected_rpl_comparison[2]
        if scenario != "historical"
        else "N/A",
        "per_rpl_500": hazard_expected_rpl_comparison[3]
        if scenario != "historical"
        else "N/A",
        "per_rpl_400": hazard_expected_rpl_comparison[4]
        if scenario != "historical"
        else "N/A",
        "per_rpl_250": hazard_expected_rpl_comparison[5]
        if scenario != "historical"
        else "N/A",
        "per_rpl_200": hazard_expected_rpl_comparison[6]
        if scenario != "historical"
        else "N/A",
        "per_rpl_150": hazard_expected_rpl_comparison[7]
        if scenario != "historical"
        else "N/A",
        "per_rpl_100": hazard_expected_rpl_comparison[8]
        if scenario != "historical"
        else "N/A",
        "per_rpl_50": hazard_expected_rpl_comparison[9]
        if scenario != "historical"
        else "N/A",
        "per_rpl_10": hazard_expected_rpl_comparison[10]
        if scenario != "historical"
        else "N/A",
    }

    # Render context into template's placeholders
    report_template.render(context)
    # Save document as .docx
    report_template.save(filepath)

    CoInitialize()

    # Convert document to .pdf
    convert(filepath)

    # Remove not necessary .docx file
    remove(path.join(DATA_REPORTS_DIR, f"{filename}.docx"))
