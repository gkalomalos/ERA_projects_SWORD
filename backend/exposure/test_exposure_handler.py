"""
Module for testing exposure data and operations.
"""

import unittest
from unittest.mock import MagicMock, mock_open, patch

from climada.entity import Exposures, Entity

from backend.constants import DATA_EXPOSURES_DIR
from backend.exposure.exposure_handler import ExposureHandler


class TestExposureHandler(unittest.TestCase):
    """
    Class for testing exposure data and operations.
    """

    def setUp(self):
        # Setup code before each test method
        self.handler = ExposureHandler()

    @patch("exposure_handler.Client")
    def test_get_exposure_success(self, mock_client):
        # Mocking the client and its response
        mock_exposure = Exposures()
        mock_client.return_value.get_litpop.return_value = mock_exposure

        country = "test_country"
        result = self.handler.get_exposure(country)

        self.assertIs(result, mock_exposure)
        mock_client.return_value.get_litpop.assert_called_once_with(
            country=country, exponents=(1, 1), dump_dir=DATA_EXPOSURES_DIR
        )

    @patch("exposure_handler.Client")
    def test_get_exposure_exception(self, mock_client):
        # Testing exception handling
        mock_client.return_value.get_litpop.side_effect = Exception("Error message")

        with self.assertRaises(ValueError):
            self.handler.get_exposure("test_country")

    @patch("exposure_handler.deepcopy")
    @patch("exposure_handler.Exposures")
    def test_get_growth_exposure(self, mock_exposures, mock_deepcopy):
        mock_exposure = MagicMock(spec=Exposures)
        mock_exposure.ref_year = 2020
        mock_exposure.gdf = MagicMock()
        mock_exposure.gdf.__getitem__.return_value = [100]
        mock_deepcopy.return_value = mock_exposure

        result = self.handler.get_growth_exposure(mock_exposure, 0.02, 2025)

        self.assertIsNotNone(result)
        self.assertEqual(result.ref_year, 2025)

    @patch("exposure_handler.json.dump")
    @patch("exposure_handler.open", new_callable=mock_open)
    @patch("exposure_handler.gpd.read_file")
    @patch("exposure_handler.get_iso3_country_code")
    def test_generate_exposure_geojson(
        self, mock_get_iso3, mock_read_file, mock_open, mock_json_dump
    ):
        mock_get_iso3.return_value = "TST"
        mock_read_file.return_value = MagicMock()
        mock_exposure = MagicMock(spec=Exposures)
        mock_exposure.gdf = MagicMock()
        mock_exposure.gdf.__geo_interface__ = {"features": []}

        self.handler.generate_exposure_geojson(mock_exposure, "Testland")

        mock_open.assert_called_once()
        mock_json_dump.assert_called_once()

    @patch("exposure_handler.Entity.from_excel")
    def test_get_entity_from_xlsx(self, mock_from_excel):
        mock_entity = MagicMock(spec=Entity)
        mock_from_excel.return_value = mock_entity
        filepath = "test.xlsx"

        result = self.handler.get_entity_from_xlsx(filepath)

        self.assertIs(result, mock_entity)
        mock_from_excel.assert_called_once_with(DATA_EXPOSURES_DIR / filepath)


if __name__ == "__main__":
    unittest.main()
