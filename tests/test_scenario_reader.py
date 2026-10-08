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
from qgis_deployment_toolbelt.__about__ import __version_clean__
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

    def test_qdt_min_version_satisfied(self):
        """Test qdt_min_version metadata when the running QDT version is recent
        enough."""
        reader = ScenarioReader(
            in_yaml="tests/fixtures/scenarios/good_scenario_sample.qdt.yml"
        )
        is_compatible, error_message = reader.is_qdt_version_compatible()
        self.assertTrue(is_compatible)
        self.assertIsNone(error_message)

        valid, report = reader.validate_scenario()
        self.assertTrue(valid)
        self.assertEqual(report, [])

    def test_qdt_min_version_too_high(self):
        """Test qdt_min_version metadata when it's higher than the running QDT
        version."""
        reader = ScenarioReader(
            in_yaml="tests/fixtures/scenarios/bad_scenario_qdt_min_version_too_high.qdt.yml"
        )
        is_compatible, error_message = reader.is_qdt_version_compatible()
        self.assertFalse(is_compatible)
        self.assertIsNotNone(error_message)
        self.assertIn(__version_clean__, error_message)

        valid, report = reader.validate_scenario()
        self.assertFalse(valid)
        self.assertEqual(len(report), 1)

    def test_qdt_min_version_invalid(self):
        """Test qdt_min_version metadata when it's not a valid version specifier."""
        reader = ScenarioReader(
            in_yaml="tests/fixtures/scenarios/bad_scenario_qdt_min_version_invalid.qdt.yml"
        )
        is_compatible, error_message = reader.is_qdt_version_compatible()
        self.assertIsNone(is_compatible)
        self.assertIsNotNone(error_message)

        valid, report = reader.validate_scenario()
        self.assertFalse(valid)
        self.assertEqual(len(report), 1)

    def test_qdt_min_version_absent(self):
        """Test qdt_min_version metadata when it's not set: scenario should
        remain valid."""
        for i in self.good_scenario_files:
            reader = ScenarioReader(in_yaml=i)
            if "qdt_min_version" not in reader.metadata:
                is_compatible, error_message = reader.is_qdt_version_compatible()
                self.assertTrue(is_compatible)
                self.assertIsNone(error_message)

    def test_summary_with_description(self):
        """Summary includes title, id and description when the latter is set."""
        reader = ScenarioReader(
            in_yaml=Path("tests/fixtures/scenarios/good_scenario_sample.qdt.yml")
        )
        summary = reader.summary
        self.assertTrue(summary.startswith(f"{reader.metadata['title']} "))
        self.assertIn(f"({reader.metadata['id']}).", summary)
        self.assertIn(reader.metadata["description"].strip()[:20], summary)

    def test_summary_without_description(self):
        """`metadata.description` is optional: no KeyError, no trailing text."""
        reader = ScenarioReader(
            in_yaml=Path(
                "tests/fixtures/scenarios/scenario_metadata_without_description.qdt.yml"
            )
        )
        self.assertNotIn("description", reader.metadata)
        valid, _ = reader.validate_scenario()
        self.assertTrue(valid)
        self.assertEqual(
            reader.summary,
            "Test scenario of QDT without description "
            "(test-scenario-without-description).",
        )

    def test_summary_with_empty_description(self):
        """An empty or null description is handled like a missing one."""
        reader = ScenarioReader(
            in_yaml=Path(
                "tests/fixtures/scenarios/scenario_metadata_without_description.qdt.yml"
            )
        )
        for empty in (None, "", "  \n"):
            reader.scenario["metadata"]["description"] = empty
            self.assertTrue(
                reader.summary.endswith("(test-scenario-without-description).")
            )

    def test_summary_without_metadata(self):
        """No metadata dict, no summary."""
        reader = ScenarioReader(
            in_yaml=Path(
                "tests/fixtures/scenarios/scenario_metadata_without_description.qdt.yml"
            )
        )
        reader.scenario["metadata"] = None
        self.assertIsNone(reader.summary)

    def test_validate_missing_required_metadata(self):
        """`metadata.id` and `metadata.title` are required by the schema."""
        path = Path(
            "tests/fixtures/scenarios/scenario_metadata_without_description.qdt.yml"
        )
        for key in ("id", "title"):
            for value in ("absent", None, "  "):
                reader = ScenarioReader(in_yaml=path)
                if value == "absent":
                    del reader.scenario["metadata"][key]
                else:
                    reader.scenario["metadata"][key] = value
                valid, report = reader.validate_scenario()
                self.assertFalse(valid, f"{key}={value!r}")
                self.assertEqual(len(report), 1)
                self.assertIn(key, report[0])
