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
from os import environ
from pathlib import Path
from posixpath import expanduser, expandvars
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

    def test_valid_with_env_var(self):
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            config_file = Path(tmpdirname).joinpath("custom_qgis_global_settings.ini")
            config_file.write_text(
                "[help]\nhelpSearchPath=$HOME/offline_qgis_doc", encoding="UTF-8"
            )

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
            read_ini = dst_file.read_text("UTF-8")
            self.assertEqual(
                read_ini,
                expanduser(
                    expandvars("[help]\nhelpSearchPath = $HOME/offline_qgis_doc\n\n")
                ),
            )

    def test_valid_with_env_var_options(self):
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            environ["CUSTOM_GLOBAL_SETTINGS"] = f"{Path(tmpdirname)}"

            config_file = Path(tmpdirname).joinpath("input_qgis_global_settings.ini")
            config_file.write_text(
                "[help]\nhelpSearchPath=$HOME/offline_qgis_doc", encoding="UTF-8"
            )

            dst_file = Path(tmpdirname) / "dest" / "custom_qgis_global_settings.ini"

            job = JobGlobalConfigManager(
                {
                    "src": "$CUSTOM_GLOBAL_SETTINGS/input_qgis_global_settings.ini",
                    "dst": "$CUSTOM_GLOBAL_SETTINGS/dest/custom_qgis_global_settings.ini",
                }
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

    def test_relative_source_qdt_work_dir(self):
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            qdt_local_workdir = (
                Path(tmpdirname).joinpath("qdt_working_folder").resolve()
            )
            environ["QDT_LOCAL_WORK_DIR"] = f"{qdt_local_workdir}"
            qdt_local_workdir.mkdir(parents=True)

            # Config file related to QDT_LOCAL_WORK_DIR
            config_file = qdt_local_workdir.joinpath("custom_qgis_global_settings.ini")
            config_file.write_text("[qgis]\ncheckVersion=true")

            dst_file = Path(tmpdirname) / "dest" / "custom_qgis_global_settings.ini"

            job = JobGlobalConfigManager(
                {
                    "src": "./custom_qgis_global_settings.ini",
                    "dst": str(dst_file),
                }
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

        # clean up environment vars
        environ.pop("QDT_LOCAL_WORK_DIR")

    def test_relative_source_qdt_repository(self):
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            qdt_local_workdir = (
                Path(tmpdirname).joinpath("qdt_working_folder").resolve()
            )
            environ["QDT_LOCAL_WORK_DIR"] = f"{qdt_local_workdir}"
            environ["QDT_TMP_RUNNING_SCENARIO_ID"] = "default"
            qdt_local_workdir.mkdir(parents=True)

            qdt_downloaded_repositories = qdt_local_workdir / "repositories" / "default"
            qdt_downloaded_repositories.mkdir(parents=True)

            qdt_downloaded_repository = qdt_downloaded_repositories.joinpath(
                "myprofiles"
            )
            qdt_downloaded_repository.mkdir(parents=True)

            # Config file related to downloaded repositories
            config_file = qdt_downloaded_repository.joinpath(
                "custom_qgis_global_settings.ini"
            )
            config_file.write_text("[qgis]\ncheckVersion=true")

            dst_file = Path(tmpdirname) / "dest" / "custom_qgis_global_settings.ini"

            job = JobGlobalConfigManager(
                {
                    "src": "./myprofiles/custom_qgis_global_settings.ini",
                    "dst": str(dst_file),
                }
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

        # clean up environment vars
        environ.pop("QDT_LOCAL_WORK_DIR")
        environ.pop("QDT_TMP_RUNNING_SCENARIO_ID")

    def test_dst_copy_exception(self):
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            config_file = Path(tmpdirname).joinpath("custom_qgis_global_settings.ini")
            config_file.write_text("[qgis]\ncheckVersion=true")

            job = JobGlobalConfigManager(
                {
                    "src": str(config_file),
                    "dst": "/sys/dev/qgis_global_settings.ini",
                }
            )

            with self.assertRaises(ValueError):
                job.run()

    def test_relative_dst(self):
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            config_file = Path(tmpdirname).joinpath("custom_qgis_global_settings.ini")
            config_file.write_text("[qgis]\ncheckVersion=true")

            job = JobGlobalConfigManager(
                {
                    "src": str(config_file),
                    "dst": "../qgis_global_settings.ini",
                }
            )

            with self.assertRaises(ValueError):
                job.run()

    def test_url_src(self):
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            dst_file = Path(tmpdirname) / "dest" / "custom_qgis_global_settings.ini"

            job = JobGlobalConfigManager(
                {
                    "src": "https://raw.githubusercontent.com/qgis/QGIS/refs/heads/master/resources/qgis_global_settings.ini",
                    "dst": str(dst_file),
                }
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

    def test_invalid_src_url(self):
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            config_file = Path(tmpdirname).joinpath("custom_qgis_global_settings.ini")
            config_file.write_text("[qgis]\ncheckVersion=true")

            job = JobGlobalConfigManager(
                {
                    "src": "https://invalidrepository.com/qgis/QGIS/refs/heads/master/resources/qgis_global_settings.ini",
                    "dst": "../qgis_global_settings.ini",
                }
            )

            with self.assertRaises(ValueError):
                job.run()

    def test_default_src(self):
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            temp_qgis_exe_path = Path(tmpdirname) / "bin"
            environ["QDT_QGIS_EXE_PATH"] = f"{temp_qgis_exe_path}"

            default_qgis_global_setting_path = (
                Path(tmpdirname) / "resources" / "qgis_global_settings.ini"
            )
            default_qgis_global_setting_path.parent.mkdir()
            default_qgis_global_setting_path.write_text("[qgis]\ncheckVersion=true")

            dst_file = Path(tmpdirname) / "dest" / "custom_qgis_global_settings.ini"

            job = JobGlobalConfigManager(
                {
                    "dst": str(dst_file),
                }
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

        # clean up environment vars
        environ.pop("QDT_QGIS_EXE_PATH")

    def test_default_dst(self):
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            config_file = Path(tmpdirname).joinpath("custom_qgis_global_settings.ini")
            config_file.write_text("[qgis]\ncheckVersion=true")

            default_dst = (
                Path(tmpdirname).joinpath("qgis_global_settings.ini").resolve()
            )
            environ["QGIS_GLOBAL_SETTINGS_FILE"] = f"{default_dst}"

            job = JobGlobalConfigManager({"src": str(config_file)})

            # Run job
            job.run()

            # Check file exists
            self.assertTrue(default_dst.exists())

            # Check environment variable QGIS_GLOBAL_SETTINGS_FILE is updated
            if get_environment_variable is not None:
                self.assertEqual(
                    get_environment_variable("QGIS_GLOBAL_SETTINGS_FILE"),
                    str(default_dst),
                )

        # clean up environment vars
        environ.pop("QGIS_GLOBAL_SETTINGS_FILE")
