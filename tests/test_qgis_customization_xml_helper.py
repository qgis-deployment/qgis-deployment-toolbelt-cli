#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_qgis_customization_xml_helper
    # for specific test
    python -m unittest tests.test_qgis_customization_xml_helper.TestQgisCustomizationXmlHelper.test_set_splash_screen_new_file
"""

# standard
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from shutil import copy2
from unittest.mock import patch

# project
from qgis_deployment_toolbelt.exceptions import QgisCustomizationXmlError
from qgis_deployment_toolbelt.jobs.job_splash_screen import JobSplashScreenManager
from qgis_deployment_toolbelt.profiles.qgis_customization_xml_handler import (
    QgisCustomizationXmlHelper,
)
from qgis_deployment_toolbelt.profiles.qgis_ini_handler import QgisIniHelper


# ############################################################################
# ########## Classes #############
# ################################


class TestQgisCustomizationXmlHelper(unittest.TestCase):
    """Test module handling QGIS customization XML file (QGIS 4+)."""

    # -- Standard methods --------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """Executed when module is loaded before any test."""
        cls.fixture_xml = Path(
            "tests/fixtures/qgis_customization/QGISCUSTOMIZATION.xml"
        )

    def setUp(self):
        """Executed before each test: fake profile with a splash screen image."""
        tmp_dir = tempfile.TemporaryDirectory(
            prefix="qdt_test_customization_xml_", ignore_cleanup_errors=True
        )
        self.addCleanup(tmp_dir.cleanup)
        self.profile_dir = Path(tmp_dir.name, "QDT Viewer Mode")
        self.profile_dir.joinpath("QGIS").mkdir(parents=True)
        self.profile_dir.joinpath("images").mkdir()
        self.splash = self.profile_dir.joinpath("images", "splash.png")
        self.splash.touch()
        self.xml_path = self.profile_dir.joinpath("QGIS", "QGISCUSTOMIZATION.xml")
        self.ini_path = self.profile_dir.joinpath("QGIS", "QGISCUSTOMIZATION3.ini")
        self.expected_splash_path = f"{self.splash.parent.resolve().as_posix()}/"

    # -- Helper ------------------------------------------------------------------
    def test_set_splash_screen_new_file(self):
        """Test customization file creation."""
        xml_helper = QgisCustomizationXmlHelper(xml_filepath=self.xml_path)
        self.assertTrue(xml_helper.set_splash_screen(self.splash))
        self.assertTrue(xml_helper.is_splash_screen_set())

        self.assertTrue(
            self.xml_path.read_text(encoding="UTF8").startswith(
                "<!DOCTYPE Customization>\n"
            )
        )
        root = xml_helper.read()
        self.assertEqual(root.get("version"), "1")
        self.assertEqual(root.get("enabled"), "true")
        self.assertEqual(root.get("splashPath"), self.expected_splash_path)
        self.assertEqual(
            [(item.tag, item.get("name"), item.get("visible")) for item in root],
            [(item, item, "true") for item in xml_helper.ROOT_ITEMS],
        )

    def test_set_splash_screen_existing_file(self):
        """Test that items customized through QGIS are preserved."""
        copy2(self.fixture_xml, self.xml_path)
        xml_helper = QgisCustomizationXmlHelper(xml_filepath=self.xml_path)
        self.assertFalse(xml_helper.is_splash_screen_set())

        self.assertTrue(xml_helper.set_splash_screen(self.splash))

        root = xml_helper.read()
        self.assertEqual(root.get("enabled"), "true")
        self.assertEqual(root.get("splashPath"), self.expected_splash_path)
        self.assertEqual(
            root.find("Menus/Menu[@name='mProjectMenu']").get("visible"), "false"
        )

        # already set: file is not written again
        with patch.object(QgisCustomizationXmlHelper, "write") as mock_write:
            self.assertTrue(xml_helper.set_splash_screen(self.splash))
            mock_write.assert_not_called()

    def test_set_splash_screen_other_format_version(self):
        """Test that a file in another format version is edited, version kept."""
        self.xml_path.write_text(
            '<Customization enabled="false" version="2"/>', encoding="UTF8"
        )
        xml_helper = QgisCustomizationXmlHelper(xml_filepath=self.xml_path)

        self.assertTrue(xml_helper.set_splash_screen(self.splash))
        root = xml_helper.read()
        self.assertEqual(root.get("version"), "2")
        self.assertEqual(root.get("splashPath"), self.expected_splash_path)

    def test_remove_splash_screen(self):
        """Test splash screen removal leaves the enabled state unchanged."""
        copy2(self.fixture_xml, self.xml_path)
        xml_helper = QgisCustomizationXmlHelper(xml_filepath=self.xml_path)

        self.assertTrue(xml_helper.set_splash_screen(switch=False))
        root = xml_helper.read()
        self.assertNotIn("splashPath", root.attrib)
        self.assertEqual(root.get("enabled"), "false")

        # nothing to remove from a missing file
        self.xml_path.unlink()
        self.assertTrue(xml_helper.set_splash_screen(switch=False))
        self.assertFalse(self.xml_path.exists())

    def test_invalid_files_left_untouched(self):
        """Test that invalid or unsupported files are not modified."""
        xml_helper = QgisCustomizationXmlHelper(xml_filepath=self.xml_path)
        for content in (
            '<Customization version="1"',
            '<Other version="1"/>',
        ):
            with self.subTest(content=content):
                self.xml_path.write_text(content, encoding="UTF8")
                with self.assertRaises(QgisCustomizationXmlError):
                    xml_helper.read()
                self.assertFalse(xml_helper.set_splash_screen(self.splash))
                self.assertEqual(self.xml_path.read_text(encoding="UTF8"), content)

    def test_set_splash_screen_without_filepath(self):
        """Test that setting a splash screen requires its path."""
        with self.assertRaises(ValueError):
            QgisCustomizationXmlHelper(self.xml_path).set_splash_screen(switch=True)

    # -- Job: file targeted according to the QGIS major version -----------------
    def get_ini_helper(self, qgis_version_major: int) -> QgisIniHelper:
        """Return the settings file helper of the fake profile."""
        return QgisIniHelper(
            ini_filepath=self.profile_dir / "QGIS" / f"QGIS{qgis_version_major}.ini",
            ini_type="profile_settings",
        )

    def test_job_qgis3(self):
        """Test that QGIS 3 still uses QGISCUSTOMIZATION3.ini."""
        self.assertTrue(
            JobSplashScreenManager.set_customization_splash_screen(
                qini_helper=self.get_ini_helper(3), splash_screen_filepath=self.splash
            )
        )
        self.assertIn("splashpath=", self.ini_path.read_text(encoding="UTF8"))
        self.assertFalse(self.xml_path.exists())

    def test_job_qgis4_ini_with_splash_only(self):
        """Test that QGIS 4 converts an ini holding only a splash path to XML."""
        self.ini_path.write_text(
            "[Customization]\nsplashpath=/old/images/\n", encoding="UTF8"
        )
        self.assertTrue(
            JobSplashScreenManager.set_customization_splash_screen(
                qini_helper=self.get_ini_helper(4), splash_screen_filepath=self.splash
            )
        )
        self.assertEqual(
            ET.parse(self.xml_path).getroot().get("splashPath"),  # noqa: S314
            self.expected_splash_path,
        )

    def test_job_qgis4_ini_with_other_customizations(self):
        """Test that QGIS 4 keeps the legacy ini file holding other customizations."""
        self.ini_path.write_text(
            "[Customization]\nMenus\\mProjectMenu=false\n", encoding="UTF8"
        )
        with self.assertLogs(level="WARNING"):
            self.assertTrue(
                JobSplashScreenManager.set_customization_splash_screen(
                    qini_helper=self.get_ini_helper(4),
                    splash_screen_filepath=self.splash,
                )
            )
        self.assertFalse(self.xml_path.exists())
        self.assertIn("splashpath=", self.ini_path.read_text(encoding="UTF8"))

    def test_job_qgis4_remove(self):
        """Test that QGIS 4 removal applies to both customization files."""
        copy2(self.fixture_xml, self.xml_path)
        self.ini_path.write_text(
            "[Customization]\nsplashpath=/old/images/\n", encoding="UTF8"
        )
        ini_helper = self.get_ini_helper(4)
        self.assertTrue(
            JobSplashScreenManager.set_customization_splash_screen(
                qini_helper=ini_helper, switch=False
            )
        )
        self.assertNotIn(
            "splashPath", QgisCustomizationXmlHelper(self.xml_path).read().attrib
        )
        self.assertFalse(ini_helper.is_splash_screen_set(ini_file=self.ini_path))


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
