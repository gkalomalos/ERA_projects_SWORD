from climada.entity.measures import Measure, MeasureSet

from hazard_handler import HazardHandler
from logger_config import LoggerConfig

hazard_handler = HazardHandler()
logger = LoggerConfig(logger_types=["file"])


class CostBenefitHandler:
    def get_measures(self, adaptation_measures: list, hazard_type: str) -> list:
        hazard_code = hazard_handler.get_hazard_code(hazard_type)
        measures = []
        if adaptation_measures:
            for adaptation_measure in adaptation_measures:
                measure = self.get_measure(adaptation_measure)
                measures.append(measure)
        else:
            measure = Measure(haz_type=hazard_code, name="Measure A", cost=0)
            measures.append(measure)
        return measures

    def get_measure(adaptation_measures: dict = None) -> Measure:
        if adaptation_measures is None:
            return Measure()
        return Measure(**adaptation_measures)

    def get_measure_set(file_path, measures: list = None) -> MeasureSet:
        if file_path:
            return MeasureSet.from_excel(file_path)
        else:
            return MeasureSet(measures)
