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
import unittest
from pathlib import Path
from sys import platform as opersys

# package
from qgis_deployment_toolbelt.jobs.job_environment_variables import (
    JobEnvironmentVariables,
)
from qgis_deployment_toolbelt.utils.str2bool import str2bool


# 3rd party


# conditional imports
if opersys == "win32":
    from qgis_deployment_toolbelt.utils.win32utils import get_environment_variable
elif opersys == "linux":
    from qgis_deployment_toolbelt.utils.linux_utils import get_environment_variable


# #############################################################################
# ########## Classes ###############
# ##################################


class TestJobEnvironmentVariables(unittest.TestCase):
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
    @unittest.skipIf(opersys == "darwin", f"Not supported operating system: {opersys}.")
    def test_environment_variables_set_unset(self):
        """Test YAML loader"""
        fake_env_vars = [
            {
                "action": "add",
                "name": "QDT_TEST_ENV_VAR",
                "scope": "user",
                "value": "this is a custom value",
            },
            {
                "action": "add",
                "name": "QDT_TEST_URL_API_PLUGIN",
                "scope": "user",
                "value": "http://api.intra.net",
                "value_type": "url",
            },
            {
                "action": "add",
                "name": "QDT_TEST_FAKE_ENV_VAR_BOOL",
                "scope": "user",
                "value": True,
                "value_type": "bool",
            },
            {
                "action": "add",
                "name": "QDT_TEST_FAKE_ENV_VAR_PATH",
                "scope": "user",
                "value": "~/scripts/qgis_startup.py",
                "value_type": "path",
            },
        ]
        job_env_vars = JobEnvironmentVariables(fake_env_vars)
        job_env_vars.run()

        # check if environment variables have been set
        if opersys == "win32":
            self.assertTrue(
                str2bool(
                    get_environment_variable("QDT_TEST_FAKE_ENV_VAR_BOOL", "user")
                ),
                True,
            )
            self.assertEqual(
                get_environment_variable("QDT_TEST_FAKE_ENV_VAR_PATH"),
                str(Path("~/scripts/qgis_startup.py").expanduser().resolve()),
            )
            self.assertEqual(
                get_environment_variable("QDT_TEST_URL_API_PLUGIN"),
                "http://api.intra.net",
            )
            self.assertEqual(
                get_environment_variable("QDT_TEST_ENV_VAR"),
                "this is a custom value",
            )

            # clean up
            fake_env_vars = [
                {
                    "name": "QDT_TEST_ENV_VAR",
                    "scope": "user",
                    "action": "remove",
                },
                {
                    "name": "QDT_TEST_URL_API_PLUGIN",
                    "scope": "user",
                    "action": "remove",
                },
                {
                    "name": "QDT_TEST_FAKE_ENV_VAR_BOOL",
                    "scope": "user",
                    "action": "remove",
                },
                {
                    "name": "QDT_TEST_FAKE_ENV_VAR_PATH",
                    "scope": "user",
                    "action": "remove",
                },
            ]
            job_env_vars = JobEnvironmentVariables(fake_env_vars)
            job_env_vars.run()

            self.assertIsNone(
                get_environment_variable("QDT_TEST_FAKE_ENV_VAR_BOOL", "user")
            )
            self.assertIsNone(
                get_environment_variable("QDT_TEST_FAKE_ENV_VAR_PATH"),
            )
        elif opersys == "linux":
            self.assertTrue(
                str2bool(
                    get_environment_variable("QDT_TEST_FAKE_ENV_VAR_BOOL", "user")
                ),
                True,
            )
            self.assertEqual(
                get_environment_variable("QDT_TEST_FAKE_ENV_VAR_PATH"),
                str(Path("~/scripts/qgis_startup.py").expanduser().resolve()),
            )
            self.assertEqual(
                get_environment_variable("QDT_TEST_URL_API_PLUGIN"),
                "http://api.intra.net",
            )
            self.assertEqual(
                get_environment_variable("QDT_TEST_ENV_VAR"),
                "this is a custom value",
            )

            # clean up
            fake_env_vars = [
                {
                    "name": "QDT_TEST_ENV_VAR",
                    "scope": "user",
                    "action": "remove",
                },
                {
                    "name": "QDT_TEST_URL_API_PLUGIN",
                    "scope": "user",
                    "action": "remove",
                },
                {
                    "name": "QDT_TEST_FAKE_ENV_VAR_BOOL",
                    "scope": "user",
                    "action": "remove",
                },
                {
                    "name": "QDT_TEST_FAKE_ENV_VAR_PATH",
                    "scope": "user",
                    "action": "remove",
                },
            ]
            job_env_vars = JobEnvironmentVariables(fake_env_vars)
            job_env_vars.run()

            self.assertIsNone(
                get_environment_variable("QDT_TEST_FAKE_ENV_VAR_BOOL", "user")
            )
            self.assertIsNone(
                get_environment_variable("QDT_TEST_FAKE_ENV_VAR_PATH"),
            )

    def test_prepare_value(self):
        """Test prepare_value method"""
        job_env_vars = JobEnvironmentVariables([])
        value_test = f"tests/{Path(__file__).name}"
        self.assertEqual(
            job_env_vars.prepare_value(value=value_test, value_type="path"),
            str(Path().resolve() / value_test),
        )
        value_test = "imaginary/path"
        if opersys == "win32":
            self.assertEqual(
                job_env_vars.prepare_value(value=value_test, value_type="path"),
                str(Path().resolve() / value_test),
            )
            self.assertEqual(
                job_env_vars.prepare_value(value=[], value_type="str"),
                "[]",
            )
        else:
            self.assertEqual(
                job_env_vars.prepare_value(value=value_test, value_type="path"),
                str(Path().resolve() / value_test),
            )
            self.assertEqual(
                job_env_vars.prepare_value(value=[]),
                "[]",
            )
