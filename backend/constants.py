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

# DATA
DATA_DIR = BASE_DIR / "data"
DATA_ENTITIES_DIR = DATA_DIR / "entities"
DATA_EXPOSURES_DIR = DATA_DIR / "exposures"
DATA_HAZARDS_DIR = DATA_DIR / "hazards"
DATA_TEMP_DIR = DATA_DIR / "temp"

# LOGS
LOG_DIR = BASE_DIR / "logs"

# BACKEND
BACKEND_DIR = BASE_DIR / "backend"

# REQUIREMENTS
REQUIREMENTS_DIR = BASE_DIR / "requirements"
