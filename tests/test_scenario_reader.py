#! python3  # noqa E265

"""Usage from the repo root folder:

.. code-block:: python

    # for whole test
    python -m unittest tests.test_scenario_reader
    # for specific
    python -m unittest tests.test_scenario_reader.TestScenarioReader.test_load_from_yaml
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import unittest
from pathlib import Path

# module target
from qgis_deployment_toolbelt.scenarios.scenario_reader import ScenarioReader


# #############################################################################
# ########## Classes ###############
# ##################################


class TestScenarioReader(unittest.TestCase):
    """Test module."""

    # -- Standard methods --------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """Executed when module is loaded before any test."""
        cls.good_scenario_files = sorted(
            Path("tests/fixtures/").glob("scenarios/good_*.y*ml")
        )

    # standard methods
    def setUp(self):
        """Fixtures prepared before each test."""
        pass

    def tearDown(self):
        """Executed after each test."""
        pass

    # -- TESTS ---------------------------------------------------------
    def test_load_from_yaml(self):
        """Test YAML loader"""
        for i in self.good_scenario_files:
            reader = ScenarioReader(in_yaml=i)
            self.assertIsInstance(reader.scenario, dict)

            # scenario sections
            self.assertIn("settings", reader.scenario)
            self.assertIn("metadata", reader.scenario)
            self.assertIn("steps", reader.scenario)

            # validation
            validation = reader.validate_scenario()
            self.assertIsInstance(validation, tuple)
            self.assertEqual(len(validation), 2)
            self.assertIsInstance(validation[0], bool)
            self.assertIsInstance(validation[1], list)

            # properties
            self.assertIsInstance(reader.metadata, dict)
            self.assertIsInstance(reader.settings, dict)
            self.assertIsInstance(reader.steps, list)

    def test_missing_scenario(self):
        """Test missing scenario."""
        with self.assertRaises(TypeError):
            ScenarioReader()

        with self.assertRaises(TypeError):
            yaml_as_dict = {"metadata": {"name": "test"}}
            ScenarioReader(yaml_as_dict)
