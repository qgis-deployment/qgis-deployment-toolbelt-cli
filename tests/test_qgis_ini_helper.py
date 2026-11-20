#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_qgis_ini_helper
    # for specific test
    python -m unittest tests.test_qgis_ini_helper.TestQgisIniHelper.test_profile_load_from_json_basic
"""

# standard
import tempfile
import unittest
from configparser import ConfigParser
from pathlib import Path
from typing import IO, Any
from unittest.mock import patch

# project
from qgis_deployment_toolbelt.profiles.qgis_ini_handler import QgisIniHelper


# ############################################################################
# ########## Classes #############
# ################################


class TestQgisIniHelper(unittest.TestCase):
    """Test module handling QGIS configuration files (*.ini)."""

    # -- Standard methods --------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """Executed when module is loaded before any test."""
        cls.configuration_files = sorted(Path("tests/fixtures/").glob("**/QGIS3*.ini"))
        cls.customization_files = sorted(Path("tests/fixtures/").glob("**/QGIS3*.ini"))

    def test_load_profile_config_default(self):
        """Test profile QGIS/QGIS3.ini loader."""
        new_config_file = Path(
            "tests/fixtures/qgis_ini/default_no_customization/QGIS3.ini"
        )

        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            tmp_copy = Path(tmpdirname).joinpath(new_config_file.name)
            tmp_copy.write_text(new_config_file.read_text())

            # open temp copy
            ini_config = QgisIniHelper(ini_filepath=tmp_copy)

        self.assertEqual(ini_config.ini_type, "profile_settings")
        self.assertFalse(ini_config.is_ui_customization_enabled())

    def test_load_profile_config_qgis4(self):
        """A QGIS4.ini settings file is recognized as a profile configuration file."""
        source_config_file = Path(
            "tests/fixtures/qgis_ini/default_no_customization/QGIS3.ini"
        )

        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            tmp_copy = Path(tmpdirname).joinpath("QGIS4.ini")
            tmp_copy.write_text(source_config_file.read_text())

            ini_config = QgisIniHelper(ini_filepath=tmp_copy)

            self.assertEqual(ini_config.ini_type, "profile_settings")
            self.assertEqual(ini_config.qgis_version_major, 4)
            self.assertEqual(ini_config.profile_config_path, tmp_copy)
            # the customization file keeps its name whatever the QGIS major version
            self.assertEqual(
                ini_config.profile_customization_path.name,
                "QGISCUSTOMIZATION3.ini",
            )
            self.assertFalse(ini_config.is_ui_customization_enabled())

    def test_customization_file_points_to_matching_config_file(self):
        """The settings file guessed from a customization file follows the QGIS major
        version."""
        fixture_ini_file = Path(
            "tests/fixtures/qgis_ini/default_customization/QGISCUSTOMIZATION3.ini"
        )

        for qgis_version_major in (3, 4):
            with self.subTest(qgis_version_major=qgis_version_major):
                ini_config = QgisIniHelper(
                    ini_filepath=fixture_ini_file,
                    ini_type="profile_customization",
                    qgis_version_major=qgis_version_major,
                )
                self.assertEqual(
                    ini_config.profile_config_path.name,
                    f"QGIS{qgis_version_major}.ini",
                )
                self.assertEqual(
                    ini_config.profile_customization_path, fixture_ini_file
                )

    def test_load_profile_customization_splash_screen(self):
        """Test profile QGIS/QGIS3.ini loader."""
        fixture_ini_file = Path(
            "tests/fixtures/qgis_ini/default_customization/QGISCUSTOMIZATION3.ini"
        )

        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            tmp_copy = Path(tmpdirname).joinpath(fixture_ini_file.name)
            tmp_copy.write_text(fixture_ini_file.read_text())

            ini_customization = QgisIniHelper(ini_filepath=tmp_copy)

        self.assertEqual(ini_customization.ini_type, "profile_customization")
        ini_config = QgisIniHelper(ini_filepath=ini_customization.profile_config_path)
        self.assertEqual(ini_config.ini_type, "profile_settings")

    def test_enable_customization(self):
        """Test profile QGIS/QGIS3.ini loader."""
        fixture_ini_file = Path(
            "tests/fixtures/qgis_ini/default_no_customization/QGIS3.ini"
        )

        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            tmp_copy = Path(tmpdirname).joinpath(fixture_ini_file.name)
            tmp_copy.write_text(fixture_ini_file.read_text())

            ini_config = QgisIniHelper(ini_filepath=tmp_copy)
            self.assertFalse(ini_config.is_ui_customization_enabled())

            ini_config.set_ui_customization_enabled(switch=True)
            self.assertTrue(ini_config.is_ui_customization_enabled())

            ini_config.set_ui_customization_enabled(switch=False)
            self.assertFalse(ini_config.is_ui_customization_enabled())

    def test_enable_customization_on_unexisting_file(self):
        """Test profile QGIS/QGIS3.ini loader."""

        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            unexisting_config_file = Path(tmpdirname).joinpath("Imaginary_QGIS3.ini")
            self.assertFalse(unexisting_config_file.exists())

            ini_config = QgisIniHelper(
                ini_filepath=unexisting_config_file, ini_type="profile_settings"
            )
            self.assertFalse(ini_config.is_ui_customization_enabled())
            self.assertFalse(unexisting_config_file.exists())

            ini_config.set_ui_customization_enabled(switch=True)
            self.assertTrue(ini_config.is_ui_customization_enabled())
            self.assertTrue(unexisting_config_file.exists())

            ini_config.set_ui_customization_enabled(switch=False)
            self.assertFalse(ini_config.is_ui_customization_enabled())
            self.assertTrue(unexisting_config_file.exists())

    def test_splash_already_set(self):
        fake_config = (
            "[Customization]\nsplashpath=/home/$USER/.share/QGIS/QGIS3/images/"
        )
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            tmp_ini_customization = Path(tmpdirname).joinpath(
                "customization_with_splashpath.ini"
            )
            tmp_ini_customization.parent.mkdir(parents=True, exist_ok=True)
            tmp_ini_customization.write_text(fake_config)

            qini_helper = QgisIniHelper(
                ini_filepath=tmp_ini_customization,
                ini_type="profile_customization",
            )
            self.assertTrue(qini_helper.is_splash_screen_set())

    def test_splash_already_set_but_empty(self):
        fake_config = "[Customization]\nsplashpath="

        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            tmp_ini_customization = Path(tmpdirname).joinpath(
                "customization_with_splashpath_empty.ini"
            )
            tmp_ini_customization.parent.mkdir(parents=True, exist_ok=True)
            tmp_ini_customization.write_text(fake_config)

            qini_helper = QgisIniHelper(
                ini_filepath=tmp_ini_customization,
                ini_type="profile_customization",
            )
            self.assertFalse(qini_helper.is_splash_screen_set())

    def test_splash_not_set(self):
        fake_config = "[Customization]\nMenu\\mDatabaseMenu=false"
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            tmp_ini_customization = Path(tmpdirname).joinpath(
                "customization_with_no_splashpath_set.ini"
            )
            tmp_ini_customization.parent.mkdir(parents=True, exist_ok=True)
            tmp_ini_customization.write_text(fake_config)

            qini_helper = QgisIniHelper(
                ini_filepath=tmp_ini_customization,
                ini_type="profile_customization",
            )
            self.assertFalse(qini_helper.is_splash_screen_set())

    def test_disable_splash_already_not_set(self):
        fake_config = "[Customization]\nMenu\\mDatabaseMenu=false"
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            tmp_ini_customization = Path(tmpdirname).joinpath(
                "set_splash_path_on_customization_with_no_splashpath_set.ini"
            )
            tmp_ini_customization.parent.mkdir(parents=True, exist_ok=True)
            tmp_ini_customization.write_text(fake_config)

            qini_helper = QgisIniHelper(
                ini_filepath=tmp_ini_customization,
                ini_type="profile_customization",
            )
            self.assertFalse(qini_helper.set_splash_screen(switch=False))

    def test_disable_splash_on_unexisting_file(self):
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            not_existing_ini_customization = Path(tmpdirname).joinpath(
                "not_existing_customization.ini"
            )

            qini_helper = QgisIniHelper(
                ini_filepath=not_existing_ini_customization,
                ini_type="profile_customization",
            )
            self.assertFalse(qini_helper.set_splash_screen(switch=False))

            not_existing_ini_config = Path("QGIS3.ini")

            qini_helper = QgisIniHelper(
                ini_filepath=not_existing_ini_config, ini_type="profile_settings"
            )
            self.assertFalse(qini_helper.set_splash_screen(switch=False))

    def test_merge_existing_file(self):
        """Test merge of INI file with backup value"""
        dst_config = "[Section]\nvalue=initial_value"
        src_config = "[Section]\nvalue=new_value"
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            dst_ini_path = Path(tmpdirname).joinpath("dest.ini")
            dst_ini_path.parent.mkdir(parents=True, exist_ok=True)
            dst_ini_path.write_text(dst_config)

            dst_ini = QgisIniHelper(
                ini_filepath=dst_ini_path,
                ini_type="profile_customization",
            )

            src_ini_path = Path(tmpdirname).joinpath("src.ini")
            src_ini_path.parent.mkdir(parents=True, exist_ok=True)
            src_ini_path.write_text(src_config)

            src_ini = QgisIniHelper(
                ini_filepath=src_ini_path,
                ini_type="profile_customization",
            )

            src_ini.merge_to(dst_ini)

            cfg_parser = ConfigParser()
            cfg_parser.read(dst_ini_path)
            self.assertIn("QDT_backup_Section", cfg_parser)
            self.assertEqual("initial_value", cfg_parser["QDT_backup_Section"]["value"])
            self.assertIn("Section", cfg_parser)
            self.assertEqual("new_value", cfg_parser["Section"]["value"])

    def test_merge_not_existing_file(self):
        """Test merge of INI file with not existing file"""
        src_config = "[Section]\nvalue=new_value"
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            src_ini_path = Path(tmpdirname).joinpath("src.ini")
            src_ini_path.parent.mkdir(parents=True, exist_ok=True)
            src_ini_path.write_text(src_config)

            src_ini = QgisIniHelper(
                ini_filepath=src_ini_path,
                ini_type="profile_customization",
            )

            empty_ini_path = Path(tmpdirname).joinpath("empty.ini")
            empty_ini = QgisIniHelper(
                ini_filepath=empty_ini_path,
                ini_type="profile_customization",
            )
            src_ini.merge_to(empty_ini)

            cfg_parser = ConfigParser()
            cfg_parser.read(empty_ini_path)
            self.assertNotIn("QDT_backup_Section", cfg_parser)
            self.assertIn("Section", cfg_parser)
            self.assertEqual("new_value", cfg_parser["Section"]["value"])

    def test_merge_preserves_utf8_with_non_utf8_default_encoding(self):
        """Merge reads INI files as UTF-8 whatever the default encoding of the OS.

        Regression test for issue #951: on Windows (cp1252), accented values were
        garbled and some characters made the merge crash.
        """
        dst_config = "[app]\nrecent=D:\\Dépôt\\carte\nnote=a\u200db\n"
        src_config = "[PythonPlugins]\nfoo=true\n"

        real_open = open

        def open_with_cp1252_default(
            file: Path | str,
            mode: str = "r",
            *args: Any,
            encoding: str | None = None,
            **kwargs: Any,
        ) -> IO:
            """Simulate a Windows cp1252 locale for text files opened without an
            explicit encoding."""
            if "b" not in mode and encoding in (None, "locale"):
                encoding = "cp1252"
            return real_open(file, mode, *args, encoding=encoding, **kwargs)

        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            dst_ini_path = Path(tmpdirname).joinpath("dst", "QGIS4.ini")
            dst_ini_path.parent.mkdir(parents=True)
            dst_ini_path.write_bytes(dst_config.encode("UTF-8"))
            src_ini_path = Path(tmpdirname).joinpath("src", "QGIS4.ini")
            src_ini_path.parent.mkdir(parents=True)
            src_ini_path.write_bytes(src_config.encode("UTF-8"))

            with patch("configparser.open", open_with_cp1252_default, create=True):
                QgisIniHelper(
                    ini_filepath=src_ini_path, ini_type="profile_settings"
                ).merge_to(
                    QgisIniHelper(
                        ini_filepath=dst_ini_path, ini_type="profile_settings"
                    )
                )

            merged = dst_ini_path.read_text(encoding="UTF-8")
            self.assertIn("D:\\Dépôt\\carte", merged)
            self.assertIn("a\u200db", merged)
            self.assertIn("[PythonPlugins]", merged)

    def test_set_section_options_existing_file(self):
        """Options are set or removed without altering the rest of the file."""
        initial_config = (
            "[qgis]\nstyle=Fusion\n\n"
            "[variables]\ncurrent_user=$USER\nobsolete_option=to_remove\n"
        )
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            ini_path = Path(tmpdirname).joinpath("QGIS3.ini")
            ini_path.write_text(initial_config)

            written_path = QgisIniHelper(
                ini_filepath=ini_path, ini_type="profile_settings"
            ).set_section_options(
                section="variables",
                options={"qdt_version": "1.0.0", "obsolete_option": None},
            )

            self.assertEqual(written_path, ini_path)
            cfg_parser = ConfigParser(interpolation=None)
            cfg_parser.optionxform = str
            cfg_parser.read(ini_path)
            self.assertEqual(cfg_parser["qgis"]["style"], "Fusion")
            # no environment variables interpolation on the other values
            self.assertEqual(cfg_parser["variables"]["current_user"], "$USER")
            self.assertEqual(cfg_parser["variables"]["qdt_version"], "1.0.0")
            self.assertNotIn("obsolete_option", cfg_parser["variables"])

    def test_set_section_options_not_existing_file(self):
        """The file and the section are created when missing."""
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_ini_file_", ignore_cleanup_errors=True
        ) as tmpdirname:
            ini_path = Path(tmpdirname).joinpath("QGIS", "QGIS4.ini")

            QgisIniHelper(
                ini_filepath=ini_path, ini_type="profile_settings"
            ).set_section_options(
                section="QDT",
                options={"qdt_profile_version": "1.2.0", "qdt_profile_email": None},
            )

            self.assertTrue(ini_path.is_file())
            cfg_parser = ConfigParser(interpolation=None)
            cfg_parser.read(ini_path)
            self.assertEqual(cfg_parser["QDT"]["qdt_profile_version"], "1.2.0")
            self.assertNotIn("qdt_profile_email", cfg_parser["QDT"])


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
