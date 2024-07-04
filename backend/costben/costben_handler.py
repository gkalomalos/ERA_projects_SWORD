"""
Module for handling cost-benefit analysis operations.

This module contains the `CostBenefitHandler` class, which manages cost-benefit analysis 
operations such as retrieving measures from Excel files, loading discount rates, calculating 
cost-benefit, and plotting results.

Classes:

- `CostBenefitHandler`: 
    Class for handling cost-benefit analysis operations.

Methods:

- `get_measure_set_from_excel`: 
    Retrieve a MeasureSet object related to a specified hazard code from an Excel file.
- `get_discount_rates_from_excel`: 
    Load discount rates from an Excel file.
- `calculate_cost_benefit`: 
    Calculate cost-benefit analysis based on current and future hazard and entity data.
- `plot_waterfall`: 
    Plot a waterfall chart for the cost-benefit analysis.
- `plot_cost_benefit`: 
    Plot the cost-benefit chart for the cost-benefit analysis.
"""

from climada.engine import CostBenefit
from climada.engine.cost_benefit import risk_aai_agg
from climada.entity import DiscRates, Entity
from climada.entity.measures import MeasureSet
from climada.hazard import Hazard
import matplotlib.pyplot as plt

from constants import DATA_TEMP_DIR, REQUIREMENTS_DIR
from logger_config import LoggerConfig

logger = LoggerConfig(logger_types=["file"])


class CostBenefitHandler:
    """
    Class for handling cost-benefit analysis operations.

    This class provides methods for retrieving measures from Excel files, loading discount rates,
    calculating cost-benefit, and plotting results.
    """

    def get_measure_set_from_excel(self, hazard_code: str) -> MeasureSet:
        """
        Retrieves a MeasureSet object related to a specified hazard code from an Excel file.

        If the file is not found or no measures are found for the specified hazard code,
        the function returns None.

        :param hazard_code: The code representing the specific hazard to retrieve measures for.
        :type hazard_code: str
        :return: A MeasureSet object containing the measures associated with the hazard code,
                or None if the file is not found or no measures exist for the hazard code.
        :rtype: MeasureSet or None
        """
        measures_path = REQUIREMENTS_DIR / "adaptation_measures.xlsx"

        try:
            # Attempt to load the measure set from the Excel file adaptation_measures.xlsx
            measure_set = MeasureSet.from_excel(measures_path)
            measure_list = measure_set.get_measure(haz_type=hazard_code)

            # Check if measures were found for the given hazard code
            if measure_list:
                # If measures are found, create a new MeasureSet with them and
                # perform any necessary checks
                measure_set = MeasureSet(measure_list)
                measure_set.check()
                return measure_set
            # Log and handle the case where no measures are found for the hazard code
            # without interrupting the flow
            logger.log("info", f"No measures found for hazard type '{hazard_code}'")
            return None
        except FileNotFoundError as e:
            # Log the case where the Excel file is not found and return None to continue the flow
            logger.log(
                "error",
                f"Adaptation measures excel file not found at {measures_path}. More info: {e}",
            )
            return None
        except Exception as exc:
            # Log any unexpected errors and return None to avoid breaking the flow
            logger.log(
                "error",
                f"An unexpected error occurred while processing the Excel file. More info: {exc}",
            )
            return None

    def get_discount_rates_from_excel(self) -> DiscRates:
        """
        Load discount rates from an Excel file.

        This function loads discount rates defined in an Excel file into a DiscRates object.
        It validates the existence of the file and uses the DiscRates class method `from_excel`
        to initialize the object. It also performs a check on the loaded data before returning.

        :return: A DiscRates instance populated with data from the Excel file.
                Returns None if an error occurs during file loading or data checking.
        :raises FileNotFoundError: If the specified Excel file does not exist.
        """
        dicsount_rates_path = REQUIREMENTS_DIR / "adaptation_measures.xlsx"

        try:
            # Attempt to load the measure set from the Excel file adaptation_measures.xlsx
            discount_rates = DiscRates().from_excel(dicsount_rates_path)
            discount_rates.check()
            return discount_rates

        except FileNotFoundError as e:
            # Log the case where the Excel file is not found and return None to continue the flow
            logger.log(
                "error",
                (
                    f"Adaptation measures excel file not found at {dicsount_rates_path}. "
                    f"More info: {e}"
                ),
            )
            return None
        except Exception as exc:
            # Log any unexpected errors and return None to avoid breaking the flow
            logger.log(
                "error",
                f"An unexpected error occurred while processing the Excel file. More info: {exc}",
            )
            return None

    # Calculate cost-benefit
    def calculate_cost_benefit(
        self,
        hazard_present: Hazard,
        entity_present: Entity,
        hazard_future: Hazard = None,
        entity_future: Entity = None,
        future_year: int = None,
    ) -> CostBenefit:
        """
        Calculates the cost-benefit analysis based on current and future hazard and entity data.

        :param hazard_present: The current hazard data.
        :type hazard_present: Hazard
        :param entity_present: The current entity data.
        :type entity_present: Entity
        :param hazard_future: The future hazard data.
        :type hazard_future: Hazard
        :param entity_future: The future entity data.
        :type entity_future: Entity
        :param future_year: The year in the future for which the analysis is performed.
        :type future_year: int
        :return: A CostBenefit object with the calculation results.
        :rtype: CostBenefit

        :raises Exception: If there's an error in the cost-benefit calculation process.
        """
        try:
            cost_benefit = CostBenefit()
            cost_benefit.calc(
                hazard_present,
                entity_present,
                hazard_future,
                entity_future,
                future_year,
                risk_aai_agg,
                save_imp=True,
            )

            return cost_benefit
        except Exception as e:
            raise Exception(f"Failed to calculate cost-benefit: {e}") from e

    def plot_waterfall(
        self,
        cost_benefit: CostBenefit,
        hazard_present: Hazard,
        entity_present: Entity,
        hazard_future: Hazard,
        entity_future: Entity,
    ) -> plt.Axes:
        """
        Plots the waterfall chart for the cost-benefit analysis.

        :param cost_benefit: The cost-benefit analysis object.
        :type cost_benefit: CostBenefit
        :return: The waterfall plot axis.
        :rtype: matplotlib.axes._subplots.AxesSubplot
        """
        try:
            axis = cost_benefit.plot_waterfall(
                hazard_present,
                entity_present,
                hazard_future,
                entity_future,
                risk_func=risk_aai_agg,
            )

            filename = DATA_TEMP_DIR / "risks_waterfall_plot.png"
            plt.savefig(filename, dpi=300, bbox_inches="tight")
            plt.close()
            return axis
        except Exception as e:
            logger.log("error", f"Failed to plot waterfall chart. More info: {e}")
            raise Exception(f"Failed to plot waterfall chart: {e}") from e

    def plot_cost_benefit(self, cost_benefit: CostBenefit):
        """
        Plots the cost-benefit chart for the cost-benefit analysis.

        :param cost_benefit: The cost-benefit analysis object.
        :type cost_benefit: CostBenefit
        :return: The cost-benefit plot axis.
        :rtype: matplotlib.axes._subplots.AxesSubplot
        """
        try:
            axis = cost_benefit.plot_cost_benefit()
            axis.set_title("Cost-Benefit Analysis")
            filename = DATA_TEMP_DIR / "cost_benefit_plot.png"
            plt.savefig(filename, dpi=300, bbox_inches="tight")
            plt.close()
            return axis
        except Exception as e:
            logger.log("error", f"Failed to plot cost-benefit chart. More info: {e}")
            raise Exception(f"Failed to plot cost-benefit chart: {e}") from e
