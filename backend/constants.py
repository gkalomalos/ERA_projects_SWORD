from os import path
from pathlib import Path
import sys


def get_base_dir():
    if getattr(sys, "frozen", False):
        # We are running in a bundle (packaged by Electron)
        return Path(sys.executable).parent.parent
    else:
        # We are running in a normal Python environment (development)
        return Path(__file__).resolve().parent.parent


BASE_DIR = get_base_dir()
CLIENT_ASSETS_DIR = path.join(BASE_DIR, "assets")

# DATA
DATA_DIR = path.join(BASE_DIR, "data")
DATA_EXPOSURES_DIR = path.join(DATA_DIR, "exposures")
DATA_HAZARDS_DIR = path.join(DATA_DIR, "hazards")
DATA_REPORTS_DIR = path.join(DATA_DIR, "reports")
TEMP_DIR = Path(DATA_DIR) / "temp"

# LOGS
LOG_DIR = Path(BASE_DIR) / "logs"

# BACKEND
BACKEND_DIR = Path(BASE_DIR) / "backend"

# FRONTEND
SRC_DIR = BASE_DIR / "src"

# REQUIREMENTS
REQUIREMENTS_DIR = path.join(BASE_DIR, "requirements")
DATASETS_DIR = path.join(REQUIREMENTS_DIR, "list_dataset_infos")
RESOURCES_DIR = path.join(REQUIREMENTS_DIR, "resources")
CURRENCY_RATES = path.join(REQUIREMENTS_DIR, "currency_rates.json")
TEMPLATES_DIR = path.join(REQUIREMENTS_DIR, "templates")
SHAPEFILES_DIR = path.join(REQUIREMENTS_DIR, "shapefiles")
FEATHERS_DIR = path.join(REQUIREMENTS_DIR, "featherfiles")
TEMPLATES_PDF_FILE = path.join(TEMPLATES_DIR, "report_template.docx")
SHAPEFILES_01M_FILE = path.join(SHAPEFILES_DIR, "NUTS_RG_01M_2021_4326.shp")

LIST_OF_RCPS = ["rcp26", "rcp45", "rcp60", "rcp85"]


THREE_LETTER_EUROPEAN_EXPOSURE = {
    "DNK": "Denmark",
    "FRA": "France",
    "CZE": "Czechia",
    "CYP": "Cyprus",
    "BEL": "Belgium",
    "AUT": "Austria",
    "EST": "Estonia",
    "FIN": "Finland",
    "DEU": "Germany",
    "GRC": "Greece",
    "HUN": "Hungary",
    "ITA": "Italy",
    "LIE": "Liechtenstein",
    "LTU": "Lithuania",
    "LUX": "Luxembourg",
    "MLT": "Malta",
    "POL": "Poland",
    "PRT": "Portugal",
    "ROU": "Romania",
    "SVK": "Slovakia",
    "SVN": "Slovenia",
    "ESP": "Spain",
    "SWE": "Sweden",
    "BGR": "Bulgaria",
    "HRV": "Croatia",
    "IRL": "Ireland",
    "LVA": "Latvia",
    "NOR": "Norway",
    "ISL": "Iceland",
    "NLD": "Netherlands",
}

EEA_COUNTRIES = [
    "Austria",
    "Belgium",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czechia",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Iceland",
    "Ireland",
    "Italy",
    "Latvia",
    "Liechtenstein",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Netherlands",
    "Norway",
    "Poland",
    "Portugal",
    "Romania",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden",
    "United Kingdom",
    "Switzerland",
]
