from climada.entity import DiscRates
from climada.entity.measures import Measure, MeasureSet

from constants import DATA_ENTITIES_DIR, REQUIREMENTS_DIR
from hazard.hazard_handler import HazardHandler
from logger_config import LoggerConfig

hazard_handler = HazardHandler()
logger = LoggerConfig(logger_types=["file"])


class CostBenefitHandler:
    def get_measure_set(self, hazard_code: str, measure_names: list = None) -> MeasureSet:
        """
        Load a MeasureSet from an Excel file and optionally filter it by measure names for a specific hazard code.

        This function reads a MeasureSet from an Excel file located in the REQUIREMENTS_DIR.
        If a list of measure names is provided, it filters the MeasureSet to include only those measures
        for the specified hazard code. The function performs a validity check on the MeasureSet
        before returning it.

        :param hazard_code: The hazard code to filter measures by.
        :param measure_names: Optional list of specific measure names to include.
        :return: A MeasureSet instance, potentially filtered by the specified measure names.
        :raises FileNotFoundError: If the Excel file does not exist.
        :raises ValueError: If specified measures are not found for the hazard code.
        """
        measures_path = REQUIREMENTS_DIR / "adaptation_measures.xlsx"
        if not measures_path.exists():
            raise FileNotFoundError(f"Excel file not found at {measures_path}")

        measure_set = MeasureSet.from_excel(measures_path)

        if measure_names:
            filtered_measures = []
            for measure_name in measure_names:
                try:
                    measure = measure_set.get_measure(haz_type=hazard_code, name=measure_name)
                    if measure:
                        filtered_measures.append(measure)
                    else:
                        raise ValueError(
                            f"Measure '{measure_name}' not found for hazard '{hazard_code}'"
                        )
                except KeyError as exc:
                    raise ValueError(f"Error accessing measure '{measure_name}'. More info: {exc}")
            measure_set = MeasureSet(measure_list=filtered_measures)

        measure_set.check()

        return measure_set

    def get_discount_rates_from_excel(self, file_path: str) -> DiscRates:
        """
        Load discount rates from an Excel file.

        This function loads discount rates defined in an Excel file into a DiscRates object.
        It validates the existence of the file and uses the DiscRates class method `from_excel`
        to initialize the object. It also performs a check on the loaded data before returning.

        :param file_path: The relative path to the Excel file within DATA_ENTITIES_DIR.
        :return: A DiscRates instance populated with data from the Excel file.
                Returns None if an error occurs during file loading or data checking.
        :raises FileNotFoundError: If the specified Excel file does not exist.
        """
        full_path = DATA_ENTITIES_DIR / file_path
        if not full_path.exists():
            raise FileNotFoundError(f"The file {full_path} does not exist.")

        try:
            discount_rates = DiscRates.from_excel(full_path)
            discount_rates.check()
            return discount_rates
        except Exception as exc:
            logger.log(
                "error",
                f"An error occurred while trying to load discount rates from the Excel file. More info: {exc}",
            )
        return None
