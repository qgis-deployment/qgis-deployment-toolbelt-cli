#! python3  # noqa E265

"""Usage from the repo root folder:

.. code-block:: python

    # for whole test
    python -m unittest tests.test_job_generic
    # for specific
    python -m unittest tests.test_job_generic.TestJobGeneric.test_listing_profiles_folder
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import tempfile
import unittest
from pathlib import Path

# package
from qgis_deployment_toolbelt.exceptions import (
    JobOptionBadNameError,
    JobOptionBadValueError,
    JobOptionBadValueTypeError,
)
from qgis_deployment_toolbelt.jobs.generic_job import GenericJob
from qgis_deployment_toolbelt.profiles.qdt_profile import QdtProfile


# #############################################################################
# ########## Classes ###############
# ##################################


class TestJobGeneric(unittest.TestCase):
    """Test generic job."""

    # -- Standard methods --------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """Executed when module is loaded before any test."""
        cls.generic_job = GenericJob()

        cls.generic_job.ID = "job-test-fixture"
        cls.generic_job.OPTIONS_SCHEMA = {
            "option_one": {
                "type": str,
                "required": True,
                "default": "git",
                "condition": "startswith",
                "possible_values": ("git", "http"),
            },
            "option_two": {
                "type": (bool, int, str),
                "required": False,
                "condition": "in",
                "possible_values": ("test", "fixture"),
            },
            "option_three": {
                "type": (bool, int, str),
                "required": False,
                "condition": None,
                "possible_values": None,
            },
        }

    # -- TESTS ---------------------------------------------------------
    def test_listing_profiles_folder(self):
        """Test profiles listing."""
        fixtures_profiles_folder = Path("tests/fixtures/profiles")
        with tempfile.TemporaryDirectory(
            prefix="QDT_test_profiles_listing_",
            ignore_cleanup_errors=True,
        ) as tmpdirname:
            tmp_folder_path = Path(tmpdirname).joinpath("profiles")
            # simulate a QGIS profiles folder structure in the temp folder
            for p in fixtures_profiles_folder.glob("good_profile_*.json"):
                dest_file = tmp_folder_path.joinpath(f"test_{p.stem}/profile.json")
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                dest_file.write_text(p.read_text(encoding="UTF-8"), encoding="UTF-8")

            filtered_profiles = self.generic_job.filter_profiles_folder(
                start_parent_folder=tmp_folder_path
            )

            self.assertIsInstance(filtered_profiles, tuple)
            self.assertGreater(len(filtered_profiles), 0)

            # length must be -1 because of a profile which is excluded by a rule
            self.assertEqual(
                len(filtered_profiles),
                len(list(tmp_folder_path.glob("**/profile.json"))) - 1,
            )

    def test_get_matching_profile_from_name(self):
        """Test get_matching_profile_from_name method."""
        fixtures_profiles_folder = Path("tests/fixtures/profiles")
        with tempfile.TemporaryDirectory(
            prefix="QDT_test_get_matching_profile_",
            ignore_cleanup_errors=True,
        ) as tmpdirname:
            tmp_folder_path = Path(tmpdirname).joinpath("profiles")
            # simulate a QGIS profiles folder structure in the temp folder
            for p in fixtures_profiles_folder.glob("good_profile_*.json"):
                dest_file = tmp_folder_path.joinpath(f"test_{p.stem}/profile.json")
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                dest_file.write_text(p.read_text(encoding="UTF-8"), encoding="UTF-8")

            filtered_profiles = self.generic_job.filter_profiles_folder(
                start_parent_folder=tmp_folder_path
            )
            matching_profile = self.generic_job.get_matching_profile_from_name(
                filtered_profiles, "qdt_test_profile_minimal"
            )
            self.assertIsInstance(matching_profile, QdtProfile)

            matching_profile = self.generic_job.get_matching_profile_from_name(
                filtered_profiles, "qdt_test_profile_minimal_not_found"
            )
            self.assertIsNone(matching_profile)

    def test_validate_options_bad_input_type(self):
        """Test validate_options method"""

        # Options must be a dictionary
        with self.assertRaises(TypeError):
            self.generic_job.validate_options(options="options_test")
        with self.assertRaises(TypeError):
            self.generic_job.validate_options(options=["options_test"])

    def test_validate_options_bad_name(self):
        """Test validate_options method"""
        # bad option name
        bad_option_name = {
            "option_one": "http://fake.url",
            "option_two": "test",
            "bad_option_name": "git",
        }

        with self.assertRaises(JobOptionBadNameError):
            self.generic_job.validate_options(bad_option_name)

    def test_validate_options_bad_condition_in(self):
        """Test validate_options method"""
        # bad value condition
        bad_options_scope = {
            "option_one": "https://fake.url",
            "option_two": "bad-value-not-in-possibles",
        }

        with self.assertRaises(JobOptionBadValueError):
            self.generic_job.validate_options(bad_options_scope)

    def test_validate_options_bad_condition_startswith(self):
        """Test validate_options method"""
        # bad value condition
        bad_options_scope = {
            "option_one": "bad-startswith",
            "option_two": "user",
        }

        with self.assertRaises(JobOptionBadValueError):
            self.generic_job.validate_options(bad_options_scope)

    def test_validate_options_bad_type(self):
        """Test validate_options method"""
        # bad value type
        bad_options = {
            "option_one": True,
            "option_two": "user",
        }

        with self.assertRaises(JobOptionBadValueTypeError):
            self.generic_job.validate_options(bad_options)
