import json
import sys
from time import time

from handlers import (
    clear_temp_dir,
    initalize_data_directories,
    sanitize_country_name,
    set_map_title,
    update_progress,
)

from costben.costben_handler import CostBenefitHandler
from exposure.exposure_handler import ExposureHandler
from hazard.hazard_handler import HazardHandler
from impact.impact_handler import ImpactHandler
from logger_config import LoggerConfig


class RunScenario:
    def __init__(self, request):
        self.request = request
        self.initialize()

    def initialize(self):
        # Initialize data folder and subfolders if not exist
        initalize_data_directories()

        # Initialize logger
        self.logger = LoggerConfig(logger_types=["file"])

        # Initialize handler instances
        self.costben_handler = CostBenefitHandler()
        self.exposure_handler = ExposureHandler()
        self.hazard_handler = HazardHandler()
        self.impact_handler = ImpactHandler()

    def clear(self):
        """Clear previously generated exposure/hazard/impact maps abd temp directory"""
        clear_temp_dir()

    def run_scenario(self) -> dict:
        """
        Run a scenario based on the provided request parameters.

        :param request: A dictionary containing the request parameters.
        :type request: dict
        :return: A dictionary containing the response data and status.
        :rtype: dict
        """
        initial_time = time()
        update_progress(10, "Setting up scenario parameters...")

        # TODO: Restore. Clear previously generated exposure/hazard/impact maps and temp directory
        # self.clear()

        adaptation_measures = self.request.get("adaptationMeasures", [])
        annual_population_growth = self.request.get("annualPopulationGrowth", 0)
        annual_gdp_growth = self.request.get("annualGDPGrowth", 0)
        country_name = self.request.get("countryName", "")
        exposure_economic = self.request.get("exposureEconomic", "")
        exposure_non_economic = self.request.get("exposureNonEconomic", "")
        hazard_type = self.request.get("hazardType", "")
        scenario = self.request.get("scenario", "")
        time_horizon = self.request.get("timeHorizon", "")
        is_era = self.request.get("isEra", False)

        country_name = sanitize_country_name(country_name)
        hazard_code = self.hazard_handler.get_hazard_code(hazard_type)

        exposure_type = (
            exposure_economic if exposure_economic else exposure_non_economic
        )  # TODO: Needs redesign
        entity_filename = self.request.get("exposureFile", "")
        hazard_filename = self.request.get("hazardFile", "")

        # Clear previously generated exposure/hazard/impact maps abd temp directory
        self.clear()

        try:
            # Generate exposure objects
            update_progress(20, "Generating Exposure object...")
            exposure_future = None
            if entity_filename == "":
                # Get exposure data from API
                exposure_present = self.exposure_handler.get_exposure(country_name)
                if annual_population_growth != 0:
                    future_year = int(time_horizon)
                    exposure_future = self.exposure_handler.get_growth_exposure(
                        exposure_present, annual_population_growth, future_year
                    )
            else:
                # Get custom exposure data from xlsx file
                entity_present = self.exposure_handler.get_entity_from_xlsx(entity_filename)
                exposure_present = entity_present.exposures
                if annual_population_growth != 0:
                    future_year = int(time_horizon)
                    exposure_future = self.exposure_handler.get_growth_exposure(
                        exposure_present, annual_population_growth, future_year
                    )

            # Generate geojson data files
            update_progress(30, "Generating Exposure geojson data files...")
            self.exposure_handler.generate_exposure_geojson(exposure_present, country_name)

            # Generate hazard objects
            update_progress(40, "Generating Hazard object...")
            hazard_future = None
            if hazard_filename == "":
                hazard_present = self.hazard_handler.get_hazard(
                    hazard_type, scenario, time_horizon, country_name
                )
                if scenario != "historical":
                    hazard_future = self.hazard_handler.get_hazard(
                        hazard_type, scenario, time_horizon, country_name
                    )
            else:
                hazard_present = self.hazard_handler.get_hazard_from_xlsx(hazard_filename)
                if scenario != "historical":
                    # TODO: This needs refactoring. We need to decide on a process on how to
                    #  handle future hazard data. For now, we are using the same hazard data
                    hazard_future = self.hazard_handler.get_hazard_from_xlsx(hazard_filename)

            # Generate Hazard geojson data files
            update_progress(50, "Generating Hazard geojson data files...")
            if scenario == "historical":
                self.hazard_handler.generate_hazard_geojson(hazard_present, country_name)
            else:
                self.hazard_handler.generate_hazard_geojson(hazard_future, country_name)

            # Calculate impact
            update_progress(60, "Generating Impact object...")

            # Calculate impact function. Same impact function set is used for both present and future
            impact_function_set = self.impact_handler.calculate_impact_function_set(hazard_present)

            # Calculate present impact
            impact_present = self.impact_handler.calculate_impact(
                exposure_present, hazard_present, impact_function_set
            )
            impact_future = None
            if scenario != "historical":
                impact_future = self.impact_handler.calculate_impact(
                    exposure_present, hazard_future, impact_function_set
                )

            # Calculate impact geojson data files
            update_progress(70, "Generating Impact geojson data files...")
            if scenario == "historical":
                self.impact_handler.generate_impact_geojson(impact_present, country_name)
            else:
                self.impact_handler.generate_impact_geojson(impact_future, country_name)

            # Calculate adaptation measures
            # measure_set = costben_handler.get_measure_set(hazard_code, adaptation_measures)

            map_title = set_map_title(hazard_type, country_name, time_horizon, scenario)
        except Exception as exception:
            status = {"code": 3000, "message": str(exception)}
            response = {"data": {"mapTitle": ""}, "status": status}
            return response

        run_status_message = f"Scenario run successfully."
        update_progress(100, run_status_message)
        response = {
            "data": {"mapTitle": map_title},
            "status": {"code": 2000, "message": run_status_message},
        }
        self.logger.log("info", f"Finished running scenario in {time() - initial_time}sec.")
        return response


if __name__ == "__main__":
    request = json.loads(sys.argv[1])
    runner = RunScenario(request)
    response = runner.run_scenario(request)
    print(json.dumps(response))
