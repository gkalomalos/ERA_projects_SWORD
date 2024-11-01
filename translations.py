import json
from pathlib import Path

import pandas as pd

LOCALES_PATH = Path("src/locales")
ROOT_PATH = Path.cwd()

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


# Add this function to read back the Excel file and generate JSON files
def generate_json_from_excel(excel_file="translations.xlsx", output_dir=LOCALES_PATH):
    # Read the Excel file
    xls = pd.ExcelFile(excel_file)

    # Process each sheet and save it to JSON
    for lang in ["English", "Arabic", "Thai"]:
        df = pd.read_excel(xls, sheet_name=lang).fillna("")  # Fill NaN values with empty strings
        lang_code = lang.lower()[:2]  # Mapping sheet names to language codes

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


# Execute function to
# create_translation_excel(translation_files)

# Execute function to create JSON files from the Excel
generate_json_from_excel(output_dir=ROOT_PATH)
