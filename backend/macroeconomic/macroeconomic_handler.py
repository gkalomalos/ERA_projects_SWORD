"""
Module for handling macroeconomic data extraction and processing.

This module reads and processes data from Excel files, filters it based on provided
parameters, and prepares it for use in other parts of the application.
"""

import pandas as pd

from logger_config import LoggerConfig


class MacroeconomicHandler:
    def __init__(self):
        self.logger = LoggerConfig(logger_types=["file"])

    def get_cred_data_from_excel(
        self,
        file_path: str,
        country_name: str,
        scenario: str,
        sector: str,
        macro_variable: str,
    ) -> dict:
        """
        Reads data from an Excel file and returns it in a structured format
        for the frontend chart.

        :param file_path: The path to the Excel file.
        :param country_name: Name of the country to filter by.
        :param scenario: Scenario to filter by.
        :param sector: Sector to filter by.
        :param macro_variable: Macroeconomic variable to filter by.
        :return: A dictionary with data structured for the frontend chart.
        """
        try:
            df = pd.read_excel(file_path, sheet_name="one_plot")

            # Filter the dataframe based on request parameters
            filtered_df = df[
                (df["Country"] == country_name)
                & (df["Scenario"] == scenario)
                & (df["Sector"] == sector)
                & (df["Variable"] == macro_variable)
            ]

            # Return early if no data matches the filters
            if filtered_df.empty:
                self.logger.log("warning", "No data found for the given filters.")
                raise ValueError("No data found for the given filters")

            return {
                "years": filtered_df["Year"].tolist(),
                "with_adaptation": filtered_df["With adaptation"].tolist(),
                "without_adaptation": filtered_df["Without adaptation"].tolist(),
            }

        except ValueError as e:
            self.logger.log("error", str(e))
            raise

        except FileNotFoundError:
            self.logger.log("error", f"Macroeconomic CRED excel file not found: {file_path}")
            return {"years": [], "with_adaptation": [], "without_adaptation": []}

        except pd.errors.EmptyDataError:
            self.logger.log(
                "error", "Macroeconomic CRED excel file is empty or contains no valid data."
            )
            return {"years": [], "with_adaptation": [], "without_adaptation": []}

        except KeyError as e:
            self.logger.log(
                "error",
                f"Missing required column in the Macroeconomic CRED excel file. More info: {e}",
            )
            return {"years": [], "with_adaptation": [], "without_adaptation": []}

        except Exception as e:
            self.logger.log("error", f"Unexpected error occurred. More info: {str(e)}")
            return {"years": [], "with_adaptation": [], "without_adaptation": []}
