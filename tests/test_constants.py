#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_constants
    # for specific test
    python -m unittest tests.test_constants.TestConstants.test_constants
"""

# standard
import tempfile
import unittest
from dataclasses import is_dataclass
from os import environ, getenv, unsetenv
from os.path import expandvars
from pathlib import Path
from sys import platform as opersys

# project
from qgis_deployment_toolbelt.constants import (
    DEFAULT_QGIS_MAJOR_VERSION,
    ENV_VAR_QGIS_VERSION,
    OSConfiguration,
    get_qdt_logs_folder,
    get_qdt_working_directory,
    get_qgis_version_major,
)


# ############################################################################
# ########## Classes #############
# ################################


class TestConstants(unittest.TestCase):
    """Test package static variables."""

    def setUp(self) -> None:
        if "QDT_QGIS_EXE_PATH" in environ or getenv("QDT_QGIS_EXE_PATH"):
            unsetenv("QDT_QGIS_EXE_PATH")
            environ.pop("QDT_QGIS_EXE_PATH")

    def test_constants(self):
        """Test types."""

        os_config = OSConfiguration.from_opersys()
        self.assertIsInstance(os_config, OSConfiguration)

        self.assertIsInstance(os_config.qgis_profiles_path, Path)
        self.assertIsInstance(os_config.shortcut_extension, str)
        self.assertIsInstance(os_config.shortcut_forbidden_chars, (tuple, type(None)))
        self.assertIsInstance(os_config.shortcut_icon_extensions, tuple)

        # Check for forbidden characters in the shortcut name
        os_config_forbidden_chars = OSConfiguration(
            names_alter=["test", "fake"],
            name_python=opersys,
            shortcut_forbidden_chars=(" ", "-"),
        )
        self.assertFalse(
            os_config_forbidden_chars.valid_shortcut_name(shortcut_name="qgis-ltr 3.28")
        )
        self.assertTrue(
            os_config_forbidden_chars.valid_shortcut_name(shortcut_name="qgis_ltr_3_28")
        )

    def test_unsupported_operating_system(self):
        """Test that a bad operating system name raise an error."""
        with self.assertRaises(ValueError):
            OSConfiguration.from_opersys("fake_operating_system_name")

    def test_get_qdt_logs_folder(self):
        """Test how QDT logs folder is retrieved"""
        # default value
        self.assertEqual(
            get_qdt_logs_folder(),
            get_qdt_working_directory().joinpath("logs"),
        )

        # using environment variable
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_logs_folder_", ignore_cleanup_errors=True
        ) as tmpdirname:
            environ["QDT_LOGS_DIR"] = tmpdirname
            self.assertEqual(
                get_qdt_logs_folder(),
                Path(tmpdirname),
            )
            unsetenv("QDT_LOGS_DIR")

        # with a bad value set in environment var --> fallback to default value (and error logged)
        environ["QDT_LOGS_DIR"] = f"{Path(__file__).resolve()}"
        self.assertEqual(
            get_qdt_logs_folder(),
            get_qdt_working_directory().joinpath("logs"),
        )
        unsetenv("QDT_LOGS_DIR")

    def test_get_qdt_working_folder(self):
        """Test how QDT working folder is retrieved"""
        # using specific value
        self.assertEqual(
            get_qdt_working_directory(specific_value="~/.cache/qdt/unit-tests/"),
            Path(Path.home(), ".cache/qdt/unit-tests/"),
        )

        # using environment variable
        environ["QDT_LOCAL_WORK_DIR"] = "~/.cache/qdt/unit-tests-env-var/"
        self.assertEqual(
            get_qdt_working_directory(),
            Path(Path.home(), ".cache/qdt/unit-tests-env-var/"),
        )
        unsetenv("QDT_LOCAL_WORK_DIR")

    def test_get_qgis_bin_path(self):
        """Test get GIS exe path helper property"""
        os_config = OSConfiguration.from_opersys()
        # default value
        self.assertEqual(os_config.get_qgis_bin_path(), os_config.qgis_bin_exe_path)

    def test_get_qgis_bin_path_with_env_var_str(self):
        """Test with environment var set as str"""
        if "QDT_QGIS_EXE_PATH" in environ:
            environ.pop("QDT_QGIS_EXE_PATH")
        environ["QDT_QGIS_EXE_PATH"] = "/usr/bin/toto"
        os_config = OSConfiguration.from_opersys()
        self.assertEqual(os_config.get_qgis_bin_path(), Path("/usr/bin/toto"))

        environ.pop("QDT_QGIS_EXE_PATH")
        environ["QDT_QGIS_EXE_PATH"] = "~/qgis-ltr-bin.exe"
        os_config = OSConfiguration.from_opersys()
        self.assertEqual(
            os_config.get_qgis_bin_path(),
            Path("~/qgis-ltr-bin.exe").expanduser().resolve(),
        )

        environ.pop("QDT_QGIS_EXE_PATH")

    def test_get_qgis_bin_path_with_env_var_dict(self):
        """Test get GIS exe path helper property"""
        if "QDT_QGIS_EXE_PATH" in environ:
            environ.pop("QDT_QGIS_EXE_PATH")
        # with environment var set as dict
        d_test = {
            "linux": "/usr/bin/qgis",
            "darwin": "/usr/bin/qgis",
            "win32": "%PROGRAMFILES%/QGIS/3_22/bin/qgis-ltr-bin.exe",
        }
        environ["QDT_QGIS_EXE_PATH"] = str(d_test)

        os_config = OSConfiguration.from_opersys()

        self.assertEqual(
            os_config.get_qgis_bin_path(),
            Path(expandvars(Path(d_test.get(opersys)).expanduser())),
        )

        environ.pop("QDT_QGIS_EXE_PATH")

    def test_get_qgis_profiles_folder_custom(self):
        """Test QGIS profiles path folder."""
        if "QGIS_CUSTOM_CONFIG_PATH" in environ:
            environ.pop("QGIS_CUSTOM_CONFIG_PATH")

        custom_qgis_profiles_folder = Path("tests/fixtures/tmp/custom_qgis_config_path")
        environ["QGIS_CUSTOM_CONFIG_PATH"] = f"{custom_qgis_profiles_folder}"

        os_config: OSConfiguration = OSConfiguration.from_opersys()

        self.assertTrue(is_dataclass(os_config))
        self.assertIsInstance(os_config, OSConfiguration)

        self.assertEqual(
            os_config.qgis_profiles_path,
            custom_qgis_profiles_folder,
        )

        environ.pop("QGIS_CUSTOM_CONFIG_PATH")
        unsetenv("QGIS_CUSTOM_CONFIG_PATH")

    # -- QGIS major version ---------------------------------------------------
    def test_get_qgis_version_major(self):
        """QGIS major version is extracted from every version scheme `packaging`
        supports."""
        for qgis_version, expected_major in (
            ("3.40.11", 3),
            ("4.2.2", 4),
            ("3.40", 3),
            ("4", 4),
            (4, 4),
            # 'v' prefixed and padded versions are tolerated, as elsewhere in QDT
            ("v4.2.2", 4),
            (" 4.2.2 ", 4),
        ):
            with self.subTest(qgis_version=qgis_version):
                self.assertEqual(
                    get_qgis_version_major(qgis_version=qgis_version), expected_major
                )

    def test_get_qgis_version_major_fallbacks(self):
        """Unsupported or unparsable versions fallback to the default major version."""
        for unsupported_version in (
            "2.18.28",  # supported scheme, unsupported major version
            "5.0.0",
            "not_a_version",  # unparsable
            "",
            "4.x",
            "4.2.2-Belem",  # release name suffix is not PEP 440
        ):
            with self.subTest(qgis_version=unsupported_version):
                self.assertEqual(
                    get_qgis_version_major(qgis_version=unsupported_version),
                    DEFAULT_QGIS_MAJOR_VERSION,
                )

    def test_get_qgis_version_major_from_environment_variable(self):
        """QGIS major version is read from the environment variable set by the
        qgis-installation-finder job."""
        initial_value = getenv(ENV_VAR_QGIS_VERSION)
        try:
            environ[ENV_VAR_QGIS_VERSION] = "4.2.2"
            self.assertEqual(get_qgis_version_major(), 4)

            environ.pop(ENV_VAR_QGIS_VERSION)
            self.assertEqual(get_qgis_version_major(), DEFAULT_QGIS_MAJOR_VERSION)
        finally:
            if initial_value is not None:
                environ[ENV_VAR_QGIS_VERSION] = initial_value
            else:
                environ.pop(ENV_VAR_QGIS_VERSION, None)

    def test_qgis_profiles_path_depends_on_qgis_major_version(self):
        """Profiles folder and ini filename follow the targeted QGIS major version."""
        if "QGIS_CUSTOM_CONFIG_PATH" in environ:
            environ.pop("QGIS_CUSTOM_CONFIG_PATH")

        for operating_system_codename in ("darwin", "linux", "win32"):
            for qgis_version_major in (3, 4):
                with self.subTest(
                    operating_system_codename=operating_system_codename,
                    qgis_version_major=qgis_version_major,
                ):
                    os_config = OSConfiguration.from_opersys(
                        operating_system_codename=operating_system_codename,
                        qgis_version_major=qgis_version_major,
                    )

                    self.assertEqual(os_config.qgis_version_major, qgis_version_major)
                    self.assertEqual(
                        os_config.qgis_profiles_path,
                        os_config.qgis_user_data_path.joinpath(
                            f"QGIS{qgis_version_major}", "profiles"
                        ),
                    )
                    self.assertEqual(
                        os_config.qgis_profile_ini_filename,
                        f"QGIS{qgis_version_major}.ini",
                    )

    def test_qgis_profiles_path_custom_config_path_wins(self):
        """QGIS_CUSTOM_CONFIG_PATH is used whatever the QGIS major version."""
        custom_qgis_profiles_folder = Path("tests/fixtures/tmp/custom_qgis_config_path")
        environ["QGIS_CUSTOM_CONFIG_PATH"] = f"{custom_qgis_profiles_folder}"

        try:
            for qgis_version_major in (3, 4):
                with self.subTest(qgis_version_major=qgis_version_major):
                    os_config = OSConfiguration.from_opersys(
                        qgis_version_major=qgis_version_major
                    )
                    self.assertEqual(
                        os_config.qgis_profiles_path, custom_qgis_profiles_folder
                    )
        finally:
            environ.pop("QGIS_CUSTOM_CONFIG_PATH")
            unsetenv("QGIS_CUSTOM_CONFIG_PATH")


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
