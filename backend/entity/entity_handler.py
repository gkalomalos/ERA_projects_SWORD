from copy import deepcopy

from climada.entity import DiscRates, Entity, Exposures
from climada.entity.measures import MeasureSet
from climada.entity.impact_funcs import ImpactFuncSet
from climada.util.api_client import Client


from constants import DATA_ENTITIES_DIR
from logger_config import LoggerConfig

logger = LoggerConfig(logger_types=["file"])


class EntityHandler:
    def __init__(self):
        self.client = Client()

    def get_entity(
        self,
        exposure: Exposures,
        discount_rates: DiscRates,
        impact_function_set: ImpactFuncSet,
        measure_set: MeasureSet,
    ) -> Entity:
        """
        Initializes and returns an Entity object based on the provided exposure data,
        discount rates, impact function set, and adaptation measure set.

        :param exposure: The exposure data for the entity.
        :type exposure: Exposure
        :param discount_rates: A list of discount rates applicable to the entity.
        :type discount_rates: list
        :param impact_function_set: The set of impact functions associated with the entity.
        :type impact_function_set: ImpactFunctionSet
        :param measure_set: The set of adaptation measures applicable to the entity.
        :type measure_set: MeasureSet
        :return: An initialized Entity object.
        :rtype: Entity

        :raises ValueError: If any of the inputs are not valid or are missing necessary data.
        """
        try:
            if not exposure or not discount_rates or not impact_function_set or not measure_set:
                raise ValueError("All parameters must be provided and valid.")

            entity = Entity(exposure, discount_rates, impact_function_set, measure_set)
            return entity
        except Exception as e:
            logger.log("error", f"Failed to initialize Entity object: {e}")
            raise ValueError(f"Failed to initialize Entity object: {e}")

    def get_entity_from_xlsx(self, filepath: str) -> Entity:
        try:
            entity_filepath = DATA_ENTITIES_DIR / filepath
            entity = Entity.from_excel(entity_filepath)
            entity.check()

            columns = [
                "category_id",
                "latitude",
                "longitude",
                "value",
                "value_unit",
                "deductible",
                "cover",
                "impf_",
            ]

            exposure = entity.exposures
            exposure.gdf = exposure.gdf[columns]
            exposure.check()

            return entity
        except Exception as exc:
            logger.log(
                "error",
                f"An error occurred while trying to create entity from xlsx. More info: {exc}",
            )
            return None

    def get_future_entity(self, entity: Entity, future_year: int, aag: float) -> Entity:
        """
        Generate a future entity based on the provided entity and year.

        :param entity: The entity object to be used as a base for the future entity.
        :type entity: Entity
        :param year: The year for which the future entity should be generated.
        :type year: int
        :param aag: The annual average growth rate for the future entity.
        :type aag: float
        :return: A future entity object based on the provided entity and year.
        :rtype: Entity
        """
        try:
            present_year = entity.exposures.ref_year
            entity_future = deepcopy(entity)
            entity_future.exposures.ref_year = future_year
            number_of_years = future_year - present_year + 1
            growth = aag**number_of_years
            entity_future.exposures.gdf["value"] = entity_future.exposures.gdf["value"] * growth
            return entity_future
        except Exception as e:
            logger.log("error", f"Failed to generate future entity: {e}")
            return None
