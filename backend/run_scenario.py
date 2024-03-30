from copy import deepcopy
import json
import sys
from time import time

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
        self.clear()

        # Initialize logger
        self.logger = LoggerConfig(logger_types=["file"])

        # Initialize handler instances
        self.costben_handler = CostBenefitHandler()
        self.entity_handler = EntityHandler()
        self.exposure_handler = ExposureHandler()
        self.hazard_handler = HazardHandler()
        self.impact_handler = ImpactHandler()

        self.request = request
        self.adaptation_measures = request.get("adaptationMeasures", [])
        self.annual_population_growth = request.get("annualPopulationGrowth", 0)
        self.annual_gdp_growth = request.get("annualGDPGrowth", 0)
        self.country_name = sanitize_country_name(request.get("countryName", ""))
        self.entity_filename = request.get("exposureFile", "")
        self.exposure_economic = request.get("exposureEconomic", "")
        self.exposure_non_economic = request.get("exposureNonEconomic", "")
        self.hazard_filename = request.get("hazardFile", "")
        self.hazard_type = request.get("hazardType", "")
        self.is_era = request.get("isEra", False)
        self.scenario = request.get("scenario", "")
        self.time_horizon = request.get("timeHorizon", "")

        self.exposure_type = self.exposure_economic or self.exposure_non_economic
        self.country_code = get_iso3_country_code(self.country_name)
        # self.entity_filename = self._get_entity_filename()
        self.hazard_code = self.hazard_handler.get_hazard_code(self.hazard_type)
        # self.hazard_filename = self._get_hazard_filename()
        self.ref_year = 2024  # TODO: Adjust this to read from the request
        self.future_year = 2050  # TODO: Adjust this to read from the request
        self.aag = 1.02  # TODO: Adjust this to read from the request

        self.status_code = 2000
        self.status_message = "Scenario run successfully."

        # Clear previously generated exposure/hazard/impact maps and temp directory
        self.clear()

    def clear(self):
        """Clear previously generated exposure/hazard/impact maps and temp directory"""
        clear_temp_dir()

    def _get_entity_filename(self):
        """Get the entity filename based on the request parameters."""
        entity_filename = (
            f"entity_TODAY_{self.country_code}_{self.hazard_type}_{self.exposure_type}.xlsx"
        )
        return entity_filename

    def _get_hazard_filename(self, is_historical: bool = False) -> str:
        """Get the hazard filename based on the request parameters."""
        if is_historical:
            hazard_filename = f"hazard_{self.hazard_type}_{self.country_code}_historical.mat"
        else:
            hazard_filename = f"hazard_{self.hazard_type}_{self.country_code}_{self.scenario}.mat"
        return hazard_filename

    def _run_era_scenario(self):
        """Run the ERA scenario based on the provided request parameters."""
        self.logger.log(
            "info",
            f"Running new {'ERA' if self.is_era else 'custom'} scenario for {self.hazard_type} hazard affecting {self.exposure_type} in {self.country_name} for a {self.scenario}.",
        )
        try:
            # Get ERA entity data
            update_progress(10, "Setting up Entity objects from predefined datasets...")
            entity_filename = self._get_entity_filename()
            entity_present = self.entity_handler.get_entity_from_xlsx(entity_filename)
            entity_present.exposures.ref_year = self.ref_year
            entity_future = None
            if self.scenario != "historical":
                entity_future = self.entity_handler.get_future_entity(
                    entity=entity_present, future_year=self.future_year, aag=self.aag
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
            hazard_present = self.hazard_handler.get_hazard_from_mat(hazard_present_filename)
            hazard_future = None
            if self.scenario != "historical":
                hazard_future_filename = self._get_hazard_filename(is_historical=False)
                hazard_future = self.hazard_handler.get_hazard_from_mat(hazard_future_filename)

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
            impact_function_id = self.impact_handler.get_impact_fun_id(
                self.hazard_type, self.exposure_type
            )
            impact_function_set = self.impact_handler.get_impact_function_set(impact_function_id)
            impact_present = self.impact_handler.calculate_impact(
                exposure_present, hazard_present, impact_function_set
            )
            impact_future = None
            if self.scenario != "historical":
                impact_future = self.impact_handler.calculate_impact(
                    exposure_future, hazard_future, impact_function_set
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

        pass

    def run_scenario(self) -> dict:
        """Run the scenario based on the provided request parameters."""
        initial_time = time()
        if self.is_era:
            self._run_era_scenario()
        else:
            self._run_custom_scenario()

        map_title = set_map_title(
            self.hazard_type, self.country_name, self.time_horizon, self.scenario
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
