from os import getcwd, path

# Check running env and configure base path. (simplistic)
# Alternative IS_DEV = environ.get("NODE_ENV") == "development" can be used
# (need also to set process.env.NODE_ENV = process.env.NODE_ENV || "production";)
if path.exists(path.join(getcwd(), "resources")):
    # production
    BASE_DIR = path.join(getcwd(), "resources")
    CLIENT_ASSETS_DIR = path.join(BASE_DIR, "assets")
else:
    # development
    BASE_DIR = path.join(getcwd())  # dev
    # BASE_DIR = path.dirname(getcwd()) #ipynb
    CLIENT_ASSETS_DIR = path.join(BASE_DIR, "src", "assets")

# DATA
DATA_DIR = path.join(BASE_DIR, "data")
DATA_EXPOSURES_DIR = path.join(DATA_DIR, "exposures")
DATA_HAZARDS_DIR = path.join(DATA_DIR, "hazards")
DATA_REPORTS_DIR = path.join(DATA_DIR, "reports")

# REQUIREMENTS
REQUIREMENTS_DIR = path.join(BASE_DIR, "requirements")
DATASETS_DIR = path.join(REQUIREMENTS_DIR, "list_dataset_infos")
RESOURCES_DIR = path.join(REQUIREMENTS_DIR, "resources")
CURRENCY_RATES = path.join(REQUIREMENTS_DIR, "currency_rates.json")
TEMP_DIR = path.join(REQUIREMENTS_DIR, "temp")
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
