import json
import logging
from pathlib import Path

import pandas as pd

LOCALES_PATH = Path("src/locales")
ROOT_PATH = Path.cwd()
LOG_FILE = ROOT_PATH / "translation_validation.log"

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    filemode="w",  # Overwrite the log file each time
)

# Paths to your JSON files
translation_files = {
    "en": LOCALES_PATH / "en.json",
    "ar": LOCALES_PATH / "ar.json",
    "th": LOCALES_PATH / "th.json",
}


# Function to load JSON data
def load_json(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


# Function to create Excel with 3 tabs for languages
def create_translation_excel(translation_files, output_file="translations.xlsx"):
    # Load English data
    en_data = load_json(translation_files["en"])
    en_df = pd.DataFrame(list(en_data.items()), columns=["Key", "English"])

    # Load Arabic and Thai data
    ar_data = load_json(translation_files["ar"])
    th_data = load_json(translation_files["th"])

    # Prepare Arabic DataFrame with empty 'Arabic' column
    ar_df = pd.DataFrame(
        {
            "Key": en_data.keys(),
            "English": en_data.values(),
            "Arabic": [ar_data.get(key, "") for key in en_data.keys()],
        }
    )

    # Prepare Thai DataFrame with empty 'Thai' column
    th_df = pd.DataFrame(
        {
            "Key": en_data.keys(),
            "English": en_data.values(),
            "Thai": [th_data.get(key, "") for key in en_data.keys()],
        }
    )

    # Write to Excel with three sheets
    with pd.ExcelWriter(output_file) as writer:
        en_df.to_excel(writer, sheet_name="English", index=False)
        ar_df.to_excel(writer, sheet_name="Arabic", index=False)
        th_df.to_excel(writer, sheet_name="Thai", index=False)

    print(f"Excel file '{output_file}' created with English, Arabic, and Thai sheets.")


# Validation function
def validate_excel(excel_file="translations.xlsx"):
    original_en_data = load_json(translation_files["en"])
    xls = pd.ExcelFile(excel_file)
    is_valid = True

    for lang in ["English", "Arabic", "Thai"]:
        df = pd.read_excel(xls, sheet_name=lang).fillna("")

        if df["Key"].tolist() != list(original_en_data.keys()):
            is_valid = False
            logging.error(f"Keys in '{lang}' sheet do not match the original data.")
            for i, (key, original_key) in enumerate(zip(df["Key"], original_en_data.keys())):
                if key != original_key:
                    logging.info(
                        f"Mismatched Key at row {i + 2}: '{key}' (Expected: '{original_key}')"
                    )

        if lang == "English" and df["English"].tolist() != list(original_en_data.values()):
            is_valid = False
            logging.error(f"English values in '{lang}' sheet do not match the original data.")
            for i, (value, original_value) in enumerate(
                zip(df["English"], original_en_data.values())
            ):
                if value != original_value:
                    logging.info(
                        f"Mismatched English Value at row {i + 2}: '{value}' (Expected: '{original_value}')"
                    )

    return is_valid


# Function to create JSON files from Excel
def generate_json_from_excel(excel_file="translations.xlsx", output_dir=LOCALES_PATH):
    if not validate_excel(excel_file):
        print("Validation failed. Check the log file for details.")
        return

    xls = pd.ExcelFile(excel_file)

    # Process each sheet and save it to JSON
    for lang in ["English", "Arabic", "Thai"]:
        df = pd.read_excel(xls, sheet_name=lang).fillna("")
        lang_code = lang.lower()[:2]

        # Extract keys and values into a dictionary
        if lang == "English":
            data = dict(zip(df["Key"], df["English"]))
        else:
            data = dict(zip(df["Key"], df[lang]))

        # Define the output path
        output_path = output_dir / f"{lang_code}.json"

        # Write dictionary to JSON
        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

        print(f"Generated '{output_path}' with {len(data)} entries.")


# Execute functions
create_translation_excel(translation_files)
generate_json_from_excel(output_dir=ROOT_PATH)
