#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_utils_ini_interpolation
    # for specific test
    python -m unittest tests.test_utils_ini_interpolation.TestUtilsIniCustomInterpolation.test_ini_env_var_interpolation
"""

# standard library
import tempfile
import unittest
from configparser import ConfigParser
from getpass import getuser
from os import environ, getenv
from pathlib import Path
from sys import platform as opersys

# project
from qgis_deployment_toolbelt.utils.ini_interpolation import (
    EnvironmentVariablesInterpolation,
)


# ############################################################################
# ########## Classes #############
# ################################


class TestUtilsIniCustomInterpolation(unittest.TestCase):
    """Test custom INI values' interpolation."""

    def check_config_read_linux(self, config: ConfigParser) -> None:
        """Check config with environnement variable interpolation for linux

        Args:
            config (ConfigParser): parser to check
        """
        self.assertEqual(config.get(section="test", option="user"), getuser())
        self.assertEqual(config.get(section="test", option="user_home"), getenv("HOME"))
        self.assertEqual(
            config.get(section="test", option="fake_value_from_environment_variable"),
            getenv("QDT_TEST_ENV_VARIABLE"),
        )
        self.assertEqual(
            config.get(section="test", option="qdt_working_directory"),
            f"{config.get(section='test', option='user_home')}/.cache/qgis-deployment-toolbelt",
        )

    @unittest.skipIf(opersys == "win32", "Test specific to Linux.")
    def test_ini_env_var_interpolation_linux(self):
        """Test interpolation results."""
        fixtures_configuration = """
        [test]
        user=$USER
        user_home = $HOME
        fake_value_from_environment_variable = $QDT_TEST_ENV_VARIABLE
        qdt_working_directory = %(user_home)s/.cache/qgis-deployment-toolbelt

        """
        environ["QDT_TEST_ENV_VARIABLE"] = "TEST_VALUE"

        config = ConfigParser(interpolation=EnvironmentVariablesInterpolation())
        config.read_string(fixtures_configuration)
        self.check_config_read_linux(config=config)

        environ.pop("QDT_TEST_ENV_VARIABLE")

    @unittest.skipIf(opersys == "win32", "Test specific to Linux.")
    def test_ini_env_var_interpolation_write_linux(self):
        """Test interpolation results for ini write."""
        fixtures_configuration = """
        [test]
        user=$USER
        user_home = $HOME
        fake_value_from_environment_variable = $QDT_TEST_ENV_VARIABLE
        qdt_working_directory = %(user_home)s/.cache/qgis-deployment-toolbelt

        """
        environ["QDT_TEST_ENV_VARIABLE"] = "TEST_VALUE"

        config = ConfigParser(interpolation=EnvironmentVariablesInterpolation())
        config.read_string(fixtures_configuration)

        with tempfile.TemporaryDirectory(
            prefix="qdt_test_write_env_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            # Write new .ini : environnement variable will be written
            tmp_copy = Path(tmpdirname).joinpath("new_file.ini")
            with tmp_copy.open(mode="w") as f:
                config.write(f)
            # Check that environnement variable are replaced
            default_config_parser = ConfigParser()
            default_config_parser.read(tmp_copy)
            self.check_config_read_linux(config=default_config_parser)

        environ.pop("QDT_TEST_ENV_VARIABLE")

    def check_config_read_windows(self, config: ConfigParser) -> None:
        """Check config with environnement variable interpolation for windows

        Args:
            config (ConfigParser): parser to check
        """
        self.assertEqual(config.get(section="test", option="user"), getuser())
        self.assertEqual(
            config.get(section="test", option="user_home"), getenv("USERPROFILE")
        )
        self.assertEqual(
            config.get(section="test", option="fake_value_from_environment_variable"),
            getenv("QDT_TEST_ENV_VARIABLE"),
        )
        self.assertEqual(
            config.get(section="test", option="qdt_working_directory"),
            f"{config.get(section='test', option='user_home')}/.cache/qgis-deployment-toolbelt",
        )

    @unittest.skipIf(opersys != "win32", "Test specific to Windows.")
    def test_ini_env_var_interpolation_windows(self):
        """Test interpolation results."""
        fixtures_configuration = """
        [test]
        user = $USERNAME
        user_home = $USERPROFILE
        fake_value_from_environment_variable = $QDT_TEST_ENV_VARIABLE
        qdt_working_directory = %(user_home)s/.cache/qgis-deployment-toolbelt

        """
        environ["QDT_TEST_ENV_VARIABLE"] = "TEST_VALUE"

        config = ConfigParser(interpolation=EnvironmentVariablesInterpolation())
        config.read_string(fixtures_configuration)
        self.check_config_read_windows(config=config)

        environ.pop("QDT_TEST_ENV_VARIABLE")

    @unittest.skipIf(opersys != "win32", "Test specific to Windows.")
    def test_ini_env_var_interpolation_write_windows(self):
        """Test interpolation results."""
        fixtures_configuration = """
        [test]
        user = $USERNAME
        user_home = $USERPROFILE
        fake_value_from_environment_variable = $QDT_TEST_ENV_VARIABLE
        qdt_working_directory = %(user_home)s/.cache/qgis-deployment-toolbelt

        """
        environ["QDT_TEST_ENV_VARIABLE"] = "TEST_VALUE"

        config = ConfigParser(interpolation=EnvironmentVariablesInterpolation())
        config.read_string(fixtures_configuration)
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_write_env_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            # Write new .ini : environnement variable will be written
            tmp_copy = Path(tmpdirname).joinpath("new_file.ini")
            with tmp_copy.open(mode="w") as f:
                config.write(f)
            # Check that environnement variable are replaced
            default_config_parser = ConfigParser()
            default_config_parser.read(tmp_copy)
            self.check_config_read_windows(config=default_config_parser)

        environ.pop("QDT_TEST_ENV_VARIABLE")


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
