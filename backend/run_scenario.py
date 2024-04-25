"""
Module to handle running scenarios based on provided parameters.

This module provides functionality to run scenarios based on parameters such as hazard type,
exposure type, country name, climate scenario type, and future year.
It contains classes and methods to orchestrate the execution of ERA and custom scenarios,
conduct cost-benefit analysis, calculate impacts, generate map data files, and prepare responses.

Classes:

- `RunScenario`: 
    Orchestrates the execution of scenarios based on provided parameters.

Methods:

- `run_scenario`: 
    Entry point to run a scenario based on provided request parameters.
"""

import json
import sys
from time import time

from climada.entity import DiscRates
import numpy as np

from handlers import (
    clear_temp_dir,
    get_iso3_country_code,
    initalize_data_directories,
    sanitize_country_name,
    set_map_title,
    update_progress,
)
from costben.costben_handler import CostBenefitHandler
from entity.entity_handler import EntityHandler
from exposure.exposure_handler import ExposureHandler
from hazard.hazard_handler import HazardHandler
from impact.impact_handler import ImpactHandler
from logger_config import LoggerConfig


class RunScenario:
    def __init__(self, request):
        # Initialize data folder and subfolders if not exist
        initalize_data_directories()

        # Clear previously generated exposure/hazard/impact maps and temp directory
        self._clear()

        # Initialize logger
        self.logger = LoggerConfig(logger_types=["file"])

        # Initialize handler instances
        self.costben_handler = CostBenefitHandler()
        self.entity_handler = EntityHandler()
        self.exposure_handler = ExposureHandler()
        self.hazard_handler = HazardHandler()
        self.impact_handler = ImpactHandler()

        # Get request parameters from the UI
        self.request = request
        self.adaptation_measures = request.get("adaptationMeasures", [])
        self.annual_growth = request.get("annualGrowth", 0)
        self.country_name = sanitize_country_name(request.get("countryName", ""))
        self.entity_filename = request.get("exposureFile", "")
        self.exposure_economic = request.get("exposureEconomic", "")
        self.exposure_non_economic = request.get("exposureNonEconomic", "")
        self.hazard_filename = request.get("hazardFile", "")
        self.hazard_type = request.get("hazardType", "")
        self.is_era = request.get("isEra", False)
        self.scenario = request.get("scenario", "")
        self.time_horizon = request.get("timeHorizon", [2024, 2050])

        # Cleanse and beautify request parameters
        self.exposure_type = self.exposure_economic or self.exposure_non_economic
        self.country_code = get_iso3_country_code(self.country_name)
        self.hazard_code = self.hazard_handler.get_hazard_code(self.hazard_type)
        self.ref_year = self.time_horizon[0]  # Set to 2024 if Era project or not selected
        self.future_year = self.time_horizon[1]  # Set to 2050 if Era project or not selected

        # Set default successfult status code and message
        self.status_code = 2000
        self.status_message = "Scenario run successfully."

        # Clear previously generated maps and geojson datasets from temp directory
        self._clear()

    def _clear(self):
        """
        Clear previously generated maps and GeoJSON datasets from the temporary directory.

        This method calls the clear_temp_dir function to delete all files in the temporary directory.

        :return: None
        """
        clear_temp_dir()

    def _get_entity_filename(self) -> str:
        """
        Get the entity filename based on the request parameters.
        This helper method sets the entity filename in a specific format to be searched
        in the data/entities directory

        :return: The entity filename.
        :rtype: str
        """
        entity_filename = (
            f"entity_TODAY_{self.country_code}_{self.hazard_type}_{self.exposure_type}.xlsx"
        )
        return entity_filename

    def _get_hazard_filename(self, is_historical: bool = False) -> str:
        """
        Get the hazard filename based on the request parameters.
        This helper method sets the hazard filename in a specific format to be searched
        in the data/hazards directory

        :param is_historical: A flag indicating whether the historical hazard filename should be retrieved.
        :type is_historical: bool
        :return: The hazard filename.
        :rtype: str
        """
        if is_historical:
            if self.hazard_code == "D":
                hazard_filename = f"hazard_{self.hazard_type}_{self.country_code}_historical.mat"
            elif self.hazard_code == "FL":
                hazard_filename = f"hazard_{self.hazard_type}_{self.country_code}_historical.tif"
            elif self.hazard_code == "HW":
                hazard_filename = f"hazard_{self.hazard_type}_{self.country_code}_historical.tif"
        else:
            if self.hazard_code == "D":
                hazard_filename = (
                    f"hazard_{self.hazard_type}_{self.country_code}_{self.scenario}.mat"
                )
            elif self.hazard_code == "FL":
                hazard_filename = (
                    f"hazard_{self.hazard_type}_{self.country_code}_{self.scenario}.tif"
                )
            elif self.hazard_code == "HW":
                hazard_filename = (
                    f"hazard_{self.hazard_type}_{self.country_code}_{self.scenario}.tif"
                )
        return hazard_filename

    def _get_era_discount_rate(self) -> DiscRates:
        """
        Get the ERA project discount rate based on the request parameters.

        Calculates the ERA project discount rate based on the country name and reference year.
        Era project discount is statically calculated:
        - For Egypt, the average discount rate is 6.89%.
        - For Thailand, the average discount rate is 0.90%.
        - For other countries, the average discount rate is 0.0.

        :return: The ERA discount rates.
        :rtype: DiscRates
        """
        try:
            if self.country_name == "Egypt":
                average_disc_rate = 0.0689
            elif self.country_name == "Thailand":
                average_disc_rate = 0.0090
            else:
                average_disc_rate = 0.0

            year_range = np.arange(self.ref_year, self.future_year + 1)
            n_years = self.future_year - self.ref_year + 1
            annual_discount = np.ones(n_years) * average_disc_rate
            discount_rates = DiscRates(year_range, annual_discount)
            discount_rates.check()
            return discount_rates

        except Exception as exception:
            self.status_code = 3000
            self.status_message = (
                f"An error occurred while getting ERA discount rate. More info: {exception}"
            )
            self.logger.log(
                "error",
                f"An error occurred while getting ERA discount rate. More info: {exception}",
            )
            return None

    def _get_average_annual_growth(self) -> float:
        """
        Get the average annual growth rate based on the request parameters.

        Calculates the average annual growth rate based on the country name, exposure type,
        and whether it's an ERA project calculation.
        - If it's an ERA calculation:
            - For economic exposure assets in Egypt:
                - average annual growth: 4.00%
            - For non-economic exposure assets in Egupt:
                - average annual growth: 1.29%
            - For economic exposure assets in Thailand:
                - average annual growth: 2.94%
            - For non-economic exposure assets in Thailand:
                - average annual growth: -0.22%

        - If it's not an ERA calculation, the method returns the provided annual growth rate.

        :return: The average annual growth rate.
        :rtype: float
        """
        try:
            growth_rates = {
                "Egypt": {
                    "tree_crops": 1.04,
                    "grass_crops": 1.04,
                    "wet_markets": 1.04,
                    "grass_crops_farmers": 1.0129,
                    "tree_crops_farmers": 1.0129,
                    "buddhist_monks": 1.0129,
                    "water_users": 1.0129,
                    "roads": 1.0129,
                },
                "Thailand": {
                    "tree_crops": 1.0294,
                    "grass_crops": 1.0294,
                    "wet_markets": 1.0294,
                    "grass_crops_farmers": 0.9978,
                    "tree_crops_farmers": 0.9978,
                    "buddhist_monks": 0.9978,
                    "water_users": 0.9978,
                    "roads": 0.9978,
                },
            }
            if self.is_era:
                default_growth_rate = 1.0
                country_growth_rates = growth_rates.get(self.country_name, {})
                growth = country_growth_rates.get(self.exposure_type, default_growth_rate)
            else:
                growth = self.annual_growth

            return growth
        except Exception as e:
            self.logger.log(
                "error", f"An error occurred while setting average annual growth: More info: {e}"
            )
            return default_growth_rate  # Default growth rate

    def _run_era_scenario(self):
        """
        Run the ERA scenario based on the provided request parameters.

        This method orchestrates the execution of the ERA scenario based on the provided
        parameters. It involves setting up Entity, Exposure, and Hazard objects,
        conducting cost-benefit analysis, plotting cost-benefit charts and waterfall graphs,
        calculating present and future impacts, and generating geojson data files for
        exposure, hazard, and impact maps.

        :raises Exception: If an error occurs while running the ERA scenario.
        """
        try:
            # Get ERA entity data
            update_progress(10, "Setting up Entity objects from custom entity file...")
            entity_filename = self._get_entity_filename()
            entity_present = self.entity_handler.get_entity_from_xlsx(entity_filename)

            # Set static present year to 2024
            entity_present.exposures.ref_year = self.ref_year

            # Get custom average annual economic/population growth
            aag = self._get_average_annual_growth()

            entity_future = None
            if self.scenario != "historical":
                entity_future = self.entity_handler.get_future_entity(
                    entity_present, self.future_year, aag
                )

            # Set Exposure objects
            update_progress(20, "Setting up Exposure objects from predefined datasets...")
            exposure_present = entity_present.exposures
            exposure_future = None
            if self.scenario != "historical":
                exposure_future = entity_future.exposures

            # Get ERA hazard data
            update_progress(30, "Setting up Hazard objects from predefined datasets...")
            hazard_present_filename = self._get_hazard_filename(is_historical=True)
            hazard_present = self.hazard_handler.get_hazard(
                hazard_type=self.hazard_type, filepath=hazard_present_filename
            )
            hazard_future = None
            if self.scenario != "historical":
                hazard_future_filename = self._get_hazard_filename(is_historical=False)
                hazard_future = self.hazard_handler.get_hazard(
                    hazard_type=self.hazard_type, filepath=hazard_future_filename
                )

            # Conduct cost-benefit analysis
            update_progress(40, "Conducting cost-benefit analysis based on predefined datasets...")
            cost_benefit = self.costben_handler.calculate_cost_benefit(
                hazard_present, entity_present, hazard_future, entity_future, self.future_year
            )

            # Plot cost-benefit charts
            update_progress(50, "Plotting cost-benefit graph...")
            self.costben_handler.plot_cost_benefit(cost_benefit)
            if self.scenario != "historical":
                update_progress(55, "Plotting waterfall graph with given risk metric...")
                self.costben_handler.plot_waterfall(
                    cost_benefit, hazard_present, entity_present, hazard_future, entity_future
                )

            # Calculate present and future impact
            update_progress(60, "Setting up Impact objects from predefined datasets...")
            impact_present = self.impact_handler.calculate_impact(
                exposure_present, hazard_present, entity_present.impact_funcs
            )
            impact_future = None
            if self.scenario != "historical":
                impact_future = self.impact_handler.calculate_impact(
                    exposure_future, hazard_future, entity_future.impact_funcs
                )

            # Generate geojson data files
            update_progress(70, "Generating Exposure map data files...")
            if self.scenario == "historical":
                self.exposure_handler.generate_exposure_geojson(exposure_present, self.country_name)
            else:
                self.exposure_handler.generate_exposure_geojson(exposure_future, self.country_name)

            update_progress(80, "Generating Hazard map data files...")
            if self.scenario == "historical":
                self.hazard_handler.generate_hazard_geojson(
                    hazard_present,
                    self.country_name,
                )
            else:
                self.hazard_handler.generate_hazard_geojson(
                    hazard_future,
                    self.country_name,
                )

            # Calculate impact geojson data files
            update_progress(90, "Generating Impact map data files...")
            if self.scenario == "historical":
                self.impact_handler.generate_impact_geojson(impact_present, self.country_name)
            else:
                self.impact_handler.generate_impact_geojson(impact_future, self.country_name)

            update_progress(100, "Scenario run successfully.")

        except Exception as exception:
            self.status_code = 3000
            self.status_message = (
                f"An error occurred while running ERA scenario. More info: {exception}"
            )
            self.logger.log(
                "error", f"An error occurred while running ERA scenario. More info: {exception}"
            )

    def _run_custom_scenario(self):
        """
        Run a custom scenario based on the provided request parameters.

        This method orchestrates the execution of a custom scenario based on the provided parameters.
        It involves setting up Entity, Exposure, and Hazard objects, conducting cost-benefit analysis,
        plotting cost-benefit charts and waterfall graphs, calculating present and future impacts,
        and generating geojson data files for exposure, hazard, and impact maps.

        :raises Exception: If an error occurs while running the custom scenario.
        """
        try:
            # Get custom entity data
            update_progress(10, "Setting up Entity objects from custom datasets...")
            # Case 1: User provides a custom excel entity dataset
            if self.entity_filename:
                entity_present = self.entity_handler.get_entity_from_xlsx(self.entity_filename)
                exposure_present = entity_present.exposures
            # Case 2: User fetches exposure datasets from the CLIMADA API
            else:
                exposure_present = self.exposure_handler.get_exposure_from_api(self.country_name)

            # Set present year for custom scenario from user time horizon selection
            exposure_present.ref_year = self.ref_year

            # Get custom average annual economic/population growth from user annual growth selection
            aag = self._get_average_annual_growth()

            entity_future = None
            if self.scenario != "historical":
                # Get future Entity object based on the future year from user time horizon selection
                entity_future = self.entity_handler.get_future_entity(
                    entity_present, self.future_year, aag
                )
                if entity_present.disc_rates:
                    entity_future.disc_rates = entity_present.disc_rates

            # Set Exposure objects
            update_progress(20, "Setting up Exposure objects from custom datasets...")
            exposure_present = entity_present.exposures
            exposure_future = None
            if self.scenario != "historical":
                exposure_future = entity_future.exposures

            # Get ERA hazard data
            update_progress(30, "Setting up Hazard objects from custom datasets...")

            # Case 1: User loads hazard dataset
            if self.hazard_filename:
                hazard_present = self.hazard_handler.get_hazard(
                    hazard_type=self.hazard_type, filepath=self.hazard_filename
                )
            # Case 2: User fetches hazard datasets from the CLIMADA API
            else:
                hazard_present = self.hazard_handler.get_hazard(
                    hazard_type=self.hazard_type,
                    source="climada_api",
                    scenario=self.scenario,
                    time_horizon=self.time_horizon,  # TODO: This won't work with CLIMADA's predefind ref years
                    country=self.country_name,
                )

            hazard_future = None
            if self.scenario != "historical":
                # Case 1: User loads hazard dataset
                if self.hazard_filename:
                    hazard_future = self.hazard_handler.get_hazard(
                        hazard_type=self.hazard_type, filepath=self.hazard_filename
                    )
                # Case 2: User fetches hazard datasets from the CLIMADA API
                else:
                    hazard_future = self.hazard_handler.get_hazard(
                        hazard_type=self.hazard_type,
                        source="climada_api",
                        scenario=self.scenario,
                        time_horizon=self.time_horizon,  # TODO: This won't work with CLIMADA's predefind ref years
                        country=self.country_name,
                    )

            # Conduct cost-benefit analysis
            update_progress(40, "Conducting cost-benefit analysis based on custom datasets...")
            cost_benefit = self.costben_handler.calculate_cost_benefit(
                hazard_present, entity_present, hazard_future, entity_future, self.future_year
            )

            # Plot cost-benefit charts
            update_progress(50, "Plotting cost-benefit graph...")
            self.costben_handler.plot_cost_benefit(cost_benefit)
            if self.scenario != "historical":
                update_progress(55, "Plotting waterfall graph with given risk metric...")
                self.costben_handler.plot_waterfall(
                    cost_benefit, hazard_present, entity_present, hazard_future, entity_future
                )

            # Calculate present and future impact
            update_progress(60, "Setting up Impact objects from custom datasets...")
            impact_present = self.impact_handler.calculate_impact(
                exposure_present, hazard_present, entity_present.impact_funcs
            )
            impact_future = None
            if self.scenario != "historical":
                impact_future = self.impact_handler.calculate_impact(
                    exposure_future, hazard_future, entity_future.impact_funcs
                )

            # Generate geojson data files
            update_progress(70, "Generating Exposure map data files...")
            if self.scenario == "historical":
                self.exposure_handler.generate_exposure_geojson(exposure_present, self.country_name)
            else:
                self.exposure_handler.generate_exposure_geojson(exposure_future, self.country_name)

            update_progress(80, "Generating Hazard map data files...")
            if self.scenario == "historical":
                self.hazard_handler.generate_hazard_geojson(
                    hazard_present,
                    self.country_name,
                )
            else:
                self.hazard_handler.generate_hazard_geojson(
                    hazard_future,
                    self.country_name,
                )

            # Calculate impact geojson data files
            update_progress(90, "Generating Impact map data files...")
            if self.scenario == "historical":
                self.impact_handler.generate_impact_geojson(impact_present, self.country_name)
            else:
                self.impact_handler.generate_impact_geojson(impact_future, self.country_name)

            update_progress(100, "Scenario run successfully.")

        except Exception as exception:
            self.status_code = 3000
            self.status_message = (
                f"An error occurred while running custom scenario. More info: {exception}"
            )
            self.logger.log(
                "error", f"An error occurred while running custom scenario. More info: {exception}"
            )

    def run_scenario(self) -> dict:
        """
        Run the scenario based on the provided request parameters.

        This method orchestrates the execution of a scenario based on the provided parameters.
        It determines whether to run an ERA scenario or a custom scenario and delegates the execution accordingly.
        After running the scenario, it sets the map title and prepares the response data.

        :return: A dictionary containing the scenario data and status information.
        :rtype: dict
        """
        initial_time = time()
        self.logger.log(
            "info",
            f"Running new {'ERA' if self.is_era else 'custom'} scenario for {self.hazard_type} hazard affecting {self.exposure_type} in {self.country_name} for a {self.scenario}.",
        )
        if self.is_era:
            self._run_era_scenario()
        else:
            self._run_custom_scenario()

        map_title = set_map_title(
            self.hazard_type, self.country_name, self.future_year, self.scenario
        )
        response = {
            "data": {"mapTitle": map_title},
            "status": {"code": self.status_code, "message": self.status_message},
        }
        self.logger.log("info", f"Finished running scenario in {time() - initial_time}sec.")
        return response


if __name__ == "__main__":
    request = json.loads(sys.argv[1])
    runner = RunScenario(request)
    response = runner.run_scenario(request)
    print(json.dumps(response))
