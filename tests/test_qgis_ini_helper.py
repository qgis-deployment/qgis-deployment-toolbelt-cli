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

        self.assertEqual(ini_config.ini_type, "profile_qgis3")
        self.assertFalse(ini_config.is_ui_customization_enabled())

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

        self.assertEqual(ini_customization.ini_type, "profile_qgis3customization")
        ini_config = QgisIniHelper(ini_filepath=ini_customization.profile_config_path)
        self.assertEqual(ini_config.ini_type, "profile_qgis3")

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
                ini_filepath=unexisting_config_file, ini_type="profile_qgis3"
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
                ini_type="profile_qgis3customization",
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
                ini_type="profile_qgis3customization",
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
                ini_type="profile_qgis3customization",
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
                ini_type="profile_qgis3customization",
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
                ini_type="profile_qgis3customization",
            )
            self.assertFalse(qini_helper.set_splash_screen(switch=False))

            not_existing_ini_config = Path("QGIS3.ini")

            qini_helper = QgisIniHelper(
                ini_filepath=not_existing_ini_config, ini_type="profile_qgis3"
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
                ini_type="profile_qgis3customization",
            )

            src_ini_path = Path(tmpdirname).joinpath("src.ini")
            src_ini_path.parent.mkdir(parents=True, exist_ok=True)
            src_ini_path.write_text(src_config)

            src_ini = QgisIniHelper(
                ini_filepath=src_ini_path,
                ini_type="profile_qgis3customization",
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
                ini_type="profile_qgis3customization",
            )

            empty_ini_path = Path(tmpdirname).joinpath("empty.ini")
            empty_ini = QgisIniHelper(
                ini_filepath=empty_ini_path,
                ini_type="profile_qgis3customization",
            )
            src_ini.merge_to(empty_ini)

            cfg_parser = ConfigParser()
            cfg_parser.read(empty_ini_path)
            self.assertNotIn("QDT_backup_Section", cfg_parser)
            self.assertIn("Section", cfg_parser)
            self.assertEqual("new_value", cfg_parser["Section"]["value"])


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
