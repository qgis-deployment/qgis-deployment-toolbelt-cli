#! python3  # noqa E265

"""Usage from the repo root folder:

.. code-block:: python

    # for whole test
    python -m unittest tests.job_qgis_installation_finder
    # for specific
    python -m unittest tests.job_qgis_installation_finder
        .TestJobQgisInstallationFinder.test_get_latest_version_from_list
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import unittest

# package
from qgis_deployment_toolbelt.jobs.job_qgis_installation_finder import (
    JobQgisInstallationFinder,
)


# 3rd party


# #############################################################################
# ########## Classes ###############
# ##################################


class TestJobQgisInstallationFinder(unittest.TestCase):
    """Test module."""

    # -- Standard methods --------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """Executed when module is loaded before any test."""

    # standard methods
    def setUp(self):
        """Fixtures prepared before each test."""
        pass

    def tearDown(self):
        """Executed after each test."""
        pass

    # -- TESTS ---------------------------------------------------------
    def test_get_latest_version_from_list(self):
        """Test definition of latest version from a list of version"""
        self.assertEqual(
            JobQgisInstallationFinder._get_latest_version_from_list(
                ["3.25.1", "4.0.1", "3.28.2"]
            ),
            "4.0.1",
        )

    def test_get_latest_matching_version_path(self):
        """Test definition of latest version from a list of version"""

        # Matching version
        self.assertEqual(
            JobQgisInstallationFinder._get_latest_matching_version_path(
                {
                    "3.25.1": "/path/to/3_25_1",
                    "3.25.8": "/path/to/3_25_8",
                    "3.25.2": "/path/to/3_25_2",
                },
                "3.25",
            ),
            "/path/to/3_25_8",
        )

        # No matching version
        self.assertIsNone(
            JobQgisInstallationFinder._get_latest_matching_version_path(
                {
                    "3.25.1": "/path/to/3_25_1",
                    "3.25.8": "/path/to/3_25_8",
                    "3.25.2": "/path/to/3_25_2",
                },
                "3.36",
            )
        )
