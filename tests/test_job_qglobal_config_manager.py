#! python3  # noqa E265

"""Usage from the repo root folder:

.. code-block:: python

    # for whole test
    python -m unittest tests.test_job_environment_variables
    # for specific
    python -m unittest tests.test_job_environment_variables
        .TestJobEnvironmentVariables.test_environment_variables_set
"""

# #############################################################################
# ########## Libraries #############
# ##################################
# Standard library
import tempfile
import unittest
from pathlib import Path
from sys import platform as opersys

# package
from qgis_deployment_toolbelt.jobs.job_qglobal_config_manager import (
    JobGlobalConfigManager,
)


# 3rd party
# conditional imports
if opersys == "win32":
    from qgis_deployment_toolbelt.utils.win32utils import get_environment_variable
elif opersys == "linux":
    from qgis_deployment_toolbelt.utils.linux_utils import get_environment_variable
else:
    get_environment_variable = None


# #############################################################################
# ########## Classes ###############
# ##################################


class TestJobGlobalConfigManager(unittest.TestCase):
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

    def test_job_id(self):
        """Test JobGlobalConfigManager id"""
        job = JobGlobalConfigManager({})
        self.assertEqual(job.ID, "qglobal-config-manager")

    def test_invalid_src(self):
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            unexisting_config_file = Path(tmpdirname).joinpath("non_existing.ini")
            self.assertFalse(unexisting_config_file.exists())

            job = JobGlobalConfigManager({"src": str(unexisting_config_file)})

            with self.assertRaises(ValueError):
                job.run()

    def test_valid(self):
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            config_file = Path(tmpdirname).joinpath("custom_qgis_global_settings.ini")
            config_file.write_text("[qgis]\ncheckVersion=true")

            dst_file = Path(tmpdirname) / "dest" / "custom_qgis_global_settings.ini"

            job = JobGlobalConfigManager(
                {"src": str(config_file), "dst": str(dst_file)}
            )

            # Run job
            job.run()

            # Check file exists
            self.assertTrue(dst_file.exists())

            # Check environment variable QGIS_GLOBAL_SETTINGS_FILE is updated
            if get_environment_variable is not None:
                self.assertEqual(
                    get_environment_variable("QGIS_GLOBAL_SETTINGS_FILE"),
                    str(dst_file),
                )
