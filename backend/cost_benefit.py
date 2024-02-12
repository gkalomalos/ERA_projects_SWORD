from climada.entity.measures import Measure, MeasureSet

from hazard import get_hazard_code
from logger_config import LoggerConfig

logger = LoggerConfig(logger_types=["file"])


def get_measures(adaptation_measures: list, hazard_type: str) -> list:
    hazard_code = get_hazard_code(hazard_type)
    measures = []
    if adaptation_measures:
        for adaptation_measure in adaptation_measures:
            measure = get_measure(adaptation_measure)
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
