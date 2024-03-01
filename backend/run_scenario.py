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
        # Initialize data folder and subfolders if not exist
        initalize_data_directories()

        # Clear previously generated exposure/hazard/impact maps and temp directory
        self.clear()

        # Initialize logger
        self.logger = LoggerConfig(logger_types=["file"])

        # Initialize handler instances
        self.costben_handler = CostBenefitHandler()
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
        self.hazard_code = self.hazard_handler.get_hazard_code(self.hazard_type)

        # Clear previously generated exposure/hazard/impact maps abd temp directory
        self.clear()

    def clear(self):
        """Clear previously generated exposure/hazard/impact maps abd temp directory"""
        clear_temp_dir()

    @classmethod
    def _run_era_scenario(self):
        
        pass

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

        try:
            # Generate exposure objects
            update_progress(20, "Generating Exposure object...")
            exposure_future = None
            if self.entity_filename == "":
                # Get exposure data from API
                exposure_present = self.exposure_handler.get_exposure(self.country_name)
                if self.annual_population_growth != 0:
                    future_year = int(self.time_horizon)
                    exposure_future = self.exposure_handler.get_growth_exposure(
                        exposure_present, self.annual_population_growth, future_year
                    )
            else:
                # Get custom exposure data from xlsx file
                entity_present = self.exposure_handler.get_entity_from_xlsx(self.entity_filename)
                exposure_present = entity_present.exposures
                if self.annual_population_growth != 0:
                    future_year = int(self.time_horizon)
                    exposure_future = self.exposure_handler.get_growth_exposure(
                        exposure_present, self.annual_population_growth, future_year
                    )

            # Generate geojson data files
            update_progress(30, "Generating Exposure geojson data files...")
            self.exposure_handler.generate_exposure_geojson(exposure_present, self.country_name)

            # Generate hazard objects
            update_progress(40, "Generating Hazard object...")
            hazard_future = None
            if self.hazard_filename == "":
                hazard_present = self.hazard_handler.get_hazard(
                    self.hazard_type, self.scenario, self.time_horizon, self.country_name
                )
                if self.scenario != "historical":
                    hazard_future = self.hazard_handler.get_hazard(
                        self.hazard_type, self.scenario, self.time_horizon, self.country_name
                    )
            else:
                hazard_present = self.hazard_handler.get_hazard_from_xlsx(self.hazard_filename)
                if self.scenario != "historical":
                    # TODO: This needs refactoring. We need to decide on a process on how to
                    #  handle future hazard data. For now, we are using the same hazard data
                    hazard_future = self.hazard_handler.get_hazard_from_xlsx(self.hazard_filename)

            # Generate Hazard geojson data files
            update_progress(50, "Generating Hazard geojson data files...")
            if self.scenario == "historical":
                self.hazard_handler.generate_hazard_geojson(hazard_present, self.country_name)
            else:
                self.hazard_handler.generate_hazard_geojson(hazard_future, self.country_name)

            # Calculate impact
            update_progress(60, "Generating Impact object...")

            # Calculate impact function. Same impact function set is used for both present and future
            impact_function_set = self.impact_handler.calculate_impact_function_set(hazard_present)

            # Calculate present impact
            impact_present = self.impact_handler.calculate_impact(
                exposure_present, hazard_present, impact_function_set
            )
            impact_future = None
            if self.scenario != "historical":
                impact_future = self.impact_handler.calculate_impact(
                    exposure_present, hazard_future, impact_function_set
                )

            # Calculate impact geojson data files
            update_progress(70, "Generating Impact geojson data files...")
            if self.scenario == "historical":
                self.impact_handler.generate_impact_geojson(impact_present, self.country_name)
            else:
                self.impact_handler.generate_impact_geojson(impact_future, self.country_name)

            # Calculate adaptation measures
            # measure_set = costben_handler.get_measure_set(hazard_code, adaptation_measures)

            map_title = set_map_title(
                self.hazard_type, self.country_name, self.time_horizon, self.scenario
            )
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
