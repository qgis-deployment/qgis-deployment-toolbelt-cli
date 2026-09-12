#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_qdt_profile_object
    # for specific test
    python -m unittest tests.test_qdt_profile_object.TestQdtProfile.test_profile_load_from_json_basic
"""

# standard
import tempfile
import unittest
from os import environ
from pathlib import Path

# project
from qgis_deployment_toolbelt.__about__ import __version_clean__
from qgis_deployment_toolbelt.profiles.qdt_profile import QdtProfile


# ############################################################################
# ########## Classes #############
# ################################


class TestQdtProfile(unittest.TestCase):
    """Test QDT profile abstraction class."""

    # -- Standard methods --------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """Executed when module is loaded before any test."""
        cls.good_profiles_files = sorted(
            Path("tests/fixtures/").glob("profiles/good_*.json")
        )

    def test_profile_load_from_json_basic(self):
        """Test profile loading from JSON."""
        for i in self.good_profiles_files:
            qdt_profile = QdtProfile.from_json(profile_json_path=i)
            self.assertIsInstance(qdt_profile, QdtProfile)

            # attributes types
            self.assertIsInstance(qdt_profile.name, str)
            self.assertIsInstance(qdt_profile.version, str)
            self.assertIsInstance(qdt_profile.plugins, list)

    def test_profile_load_from_json_with_parent_folder(self):
        """Test profile loading from JSON specifying parent folder."""
        for i in self.good_profiles_files:
            qdt_profile = QdtProfile.from_json(i, i.parent)
            self.assertIsInstance(qdt_profile, QdtProfile)

            # attributes types
            self.assertIsInstance(qdt_profile.name, str)
            self.assertIsInstance(qdt_profile.version, str)
            self.assertIsInstance(qdt_profile.plugins, list)

    def test_profile_load_from_json_complete(self):
        """Test profile loading from JSON."""
        for i in filter(lambda x: "complete" in x.name, self.good_profiles_files):
            qdt_profile = QdtProfile.from_json(i, i.parent)
            self.assertIsInstance(qdt_profile, QdtProfile)

            # attributes types
            self.assertIsInstance(qdt_profile.name, str)
            self.assertIsInstance(qdt_profile.alias, str)
            self.assertIsInstance(qdt_profile.folder, Path)
            self.assertIsInstance(qdt_profile.splash, (str, Path))
            self.assertIsInstance(qdt_profile.version, str)

            # attributes values
            self.assertEqual(i.parent.resolve(), qdt_profile.folder)

    def test_profile_versions_comparison_semver(self):
        """Test profile compare versions semver"""
        profile_v1: QdtProfile = QdtProfile(
            alias="Unit Test lesser",
            name="unit_test_1",
            version="1.0.0",
        )

        profile_v2: QdtProfile = QdtProfile(
            alias="Unit Test lesser",
            name="unit_test_1",
            version="1.1.0",
        )

        profile_v3: QdtProfile = QdtProfile(
            alias="Unit Test lesser",
            name="unit_test_1",
            version="3.1.0",
        )

        self.assertTrue(profile_v1.is_older_than(profile_v2.version))
        self.assertTrue(profile_v1.is_older_than(profile_v2))
        self.assertTrue(profile_v1.is_older_than(profile_v3.version))
        self.assertTrue(profile_v1.is_older_than(profile_v3))
        self.assertTrue(profile_v2.is_older_than(profile_v3.version))
        self.assertTrue(profile_v2.is_older_than(profile_v3))
        self.assertFalse(profile_v2.is_older_than(profile_v1))

    def test_qdt_min_version_satisfied(self):
        """Test qdtMinVersion attribute when the running QDT version is recent
        enough."""
        qdt_profile = QdtProfile.from_json(
            profile_json_path=Path(
                "tests/fixtures/profiles/good_profile_qdt_min_version_satisfied.json"
            )
        )
        is_compatible, error_message = qdt_profile.is_qdt_version_compatible()
        self.assertTrue(is_compatible)
        self.assertIsNone(error_message)

    def test_qdt_min_version_too_high(self):
        """Test qdtMinVersion attribute when it's higher than the running QDT
        version."""
        qdt_profile = QdtProfile.from_json(
            profile_json_path=Path(
                "tests/fixtures/profiles/bad_profile_qdt_min_version_too_high.json"
            )
        )
        is_compatible, error_message = qdt_profile.is_qdt_version_compatible()
        self.assertFalse(is_compatible)
        self.assertIsNotNone(error_message)
        self.assertIn(__version_clean__, error_message)

    def test_qdt_min_version_invalid(self):
        """Test qdtMinVersion attribute when it's not a valid version specifier."""
        qdt_profile = QdtProfile.from_json(
            profile_json_path=Path(
                "tests/fixtures/profiles/bad_profile_qdt_min_version_invalid.json"
            )
        )
        is_compatible, error_message = qdt_profile.is_qdt_version_compatible()
        self.assertIsNone(is_compatible)
        self.assertIsNotNone(error_message)

    def test_qdt_min_version_absent(self):
        """Test qdtMinVersion attribute when it's not set: profile should
        remain compatible."""
        for i in self.good_profiles_files:
            qdt_profile = QdtProfile.from_json(profile_json_path=i)
            if qdt_profile.qdt_min_version is None:
                is_compatible, error_message = qdt_profile.is_qdt_version_compatible()
                self.assertTrue(is_compatible)
                self.assertIsNone(error_message)

    # -- QGIS major version detection --------------------------------------------
    def test_profile_qgis_version_major_from_installed_path(self):
        """QGIS major version is deduced from the QGIS versioned parent folder."""
        for qgis_version_major in (3, 4):
            with self.subTest(qgis_version_major=qgis_version_major):
                qdt_profile = QdtProfile(
                    name="unit_test",
                    folder=Path(
                        f"/home/qdt/.local/share/QGIS/QGIS{qgis_version_major}"
                        "/profiles/unit_test"
                    ),
                )
                self.assertEqual(qdt_profile.qgis_version_major, qgis_version_major)

    def test_profile_qgis_version_major_case_insensitive(self):
        """QGIS versioned folder is matched whatever its case (Windows-friendly)."""
        qdt_profile = QdtProfile(
            name="unit_test",
            folder=Path("/home/qdt/AppData/Roaming/QGIS/qgis3/profiles/unit_test"),
        )
        self.assertEqual(qdt_profile.qgis_version_major, 3)

    def test_profile_qgis_version_major_nearest_parent_wins(self):
        """The closest QGIS versioned parent folder takes precedence."""
        qdt_profile = QdtProfile(
            name="unit_test",
            folder=Path("/data/QGIS4/backup/QGIS/QGIS3/profiles/unit_test"),
        )
        self.assertEqual(qdt_profile.qgis_version_major, 3)

    def test_profile_qgis_version_major_unsupported_version(self):
        """An out of range QGIS major version is ignored, not returned."""
        qdt_profile = QdtProfile(
            name="unit_test",
            folder=Path("/home/qdt/.local/share/QGIS/QGIS2/profiles/unit_test"),
        )
        self.assertIsNone(qdt_profile.qgis_version_major)

    def test_profile_qgis_version_major_no_versioned_parent(self):
        """A downloaded or custom-located profile has no detectable version."""
        for folder in (
            Path("/home/qdt/.cache/qgis-deployment-toolbelt/profiles/unit_test"),
            Path("/opt/qgis-custom-config/profiles/unit_test"),
            Path("/data/QGIS3-backup/profiles/unit_test"),
        ):
            with self.subTest(folder=folder):
                qdt_profile = QdtProfile(name="unit_test", folder=folder)
                self.assertIsNone(qdt_profile.qgis_version_major)

    def test_profile_qgis_version_major_without_folder(self):
        """A profile without folder does not raise and returns None."""
        qdt_profile = QdtProfile(name="unit_test", version="1.0.0")
        self.assertIsNone(qdt_profile.qgis_version_major)

    def test_profile_qgis_version_bounds(self):
        """QGIS version bounds declared in profile.json are readable."""
        qdt_profile = QdtProfile.from_json(
            profile_json_path=Path("tests/fixtures/profiles/good_profile_complete.json")
        )
        self.assertEqual(qdt_profile.qgis_minimum_version, "3.22")
        self.assertEqual(qdt_profile.qgis_maximum_version, "3.30")

        unbounded_profile = QdtProfile(name="unit_test", version="1.0.0")
        self.assertIsNone(unbounded_profile.qgis_minimum_version)
        self.assertIsNone(unbounded_profile.qgis_maximum_version)

    # -- QGIS settings file (QGIS3.ini, QGIS4.ini...) -----------------------------
    @staticmethod
    def _make_profile_with_ini(
        profile_folder: Path, ini_filenames: tuple[str, ...]
    ) -> QdtProfile:
        """Create a profile folder shipping the given QGIS settings files."""
        profile_folder.joinpath("QGIS").mkdir(parents=True, exist_ok=True)
        for ini_filename in ini_filenames:
            profile_folder.joinpath("QGIS", ini_filename).write_text(
                "[UI]\nCustomization\\enabled=false\n", encoding="UTF8"
            )
        return QdtProfile(name="unit_test", folder=profile_folder)

    def test_profile_qgis_ini_filepath_matching_version(self):
        """The settings file named after the targeted QGIS major version is used."""
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_profile_ini_", ignore_cleanup_errors=True
        ) as tmpdirname:
            qdt_profile = self._make_profile_with_ini(
                profile_folder=Path(tmpdirname),
                ini_filenames=("QGIS3.ini", "QGIS4.ini"),
            )
            qdt_profile.os_config.qgis_version_major = 4

            self.assertEqual(qdt_profile.qgis_ini_filename, "QGIS4.ini")
            self.assertEqual(qdt_profile.qgis_ini_filepath.name, "QGIS4.ini")
            self.assertTrue(qdt_profile.has_qgis_ini_file())

    def test_profile_qgis_ini_filepath_fallback_to_shipped_file(self):
        """A profile shipping only a QGIS3.ini is still handled on a QGIS 4 machine."""
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_profile_ini_", ignore_cleanup_errors=True
        ) as tmpdirname:
            qdt_profile = self._make_profile_with_ini(
                profile_folder=Path(tmpdirname), ini_filenames=("QGIS3.ini",)
            )
            qdt_profile.os_config.qgis_version_major = 4

            self.assertEqual(qdt_profile.qgis_ini_filename, "QGIS4.ini")
            self.assertEqual(qdt_profile.qgis_ini_filepath.name, "QGIS3.ini")
            self.assertTrue(qdt_profile.has_qgis_ini_file())

    def test_profile_qgis_ini_filepath_without_any_ini_file(self):
        """Without any settings file, the expected filename is returned."""
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_profile_ini_", ignore_cleanup_errors=True
        ) as tmpdirname:
            qdt_profile = self._make_profile_with_ini(
                profile_folder=Path(tmpdirname), ini_filenames=()
            )
            qdt_profile.os_config.qgis_version_major = 4

            self.assertEqual(qdt_profile.qgis_ini_filepath.name, "QGIS4.ini")
            self.assertFalse(qdt_profile.has_qgis_ini_file())

    def test_profile_rename_qgis_ini_file_to_target_version(self):
        """A QGIS3.ini shipped by a profile is renamed for a QGIS 4 target."""
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_profile_ini_", ignore_cleanup_errors=True
        ) as tmpdirname:
            qdt_profile = self._make_profile_with_ini(
                profile_folder=Path(tmpdirname), ini_filenames=("QGIS3.ini",)
            )
            qdt_profile.os_config.qgis_version_major = 4

            renamed_ini_filepath = qdt_profile.rename_qgis_ini_file_to_target_version()

            self.assertIsNotNone(renamed_ini_filepath)
            self.assertEqual(renamed_ini_filepath.name, "QGIS4.ini")
            self.assertTrue(renamed_ini_filepath.is_file())
            self.assertFalse(
                Path(tmpdirname).joinpath("QGIS", "QGIS3.ini").exists(),
            )

    def test_profile_rename_qgis_ini_file_noop(self):
        """Nothing is renamed when the settings file already has the expected name or
        when both files are shipped."""
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_profile_ini_", ignore_cleanup_errors=True
        ) as tmpdirname:
            already_ok = self._make_profile_with_ini(
                profile_folder=Path(tmpdirname).joinpath("already_ok"),
                ini_filenames=("QGIS4.ini",),
            )
            already_ok.os_config.qgis_version_major = 4
            self.assertIsNone(already_ok.rename_qgis_ini_file_to_target_version())

            both = self._make_profile_with_ini(
                profile_folder=Path(tmpdirname).joinpath("both"),
                ini_filenames=("QGIS3.ini", "QGIS4.ini"),
            )
            both.os_config.qgis_version_major = 4
            self.assertIsNone(both.rename_qgis_ini_file_to_target_version())
            self.assertTrue(
                Path(tmpdirname).joinpath("both", "QGIS", "QGIS3.ini").is_file()
            )

    def test_profile_merge_to_qgis4_installed_profile(self):
        """A profile authored for QGIS 3 lands as a QGIS4.ini into an installed profile
        of a machine running QGIS 4."""
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_profile_merge_", ignore_cleanup_errors=True
        ) as tmpdirname:
            qgis_profiles_path = Path(tmpdirname).joinpath("QGIS4", "profiles")

            # sandbox the installed profiles folder, as QGIS itself allows
            initial_custom_config_path = environ.get("QGIS_CUSTOM_CONFIG_PATH")
            environ["QGIS_CUSTOM_CONFIG_PATH"] = f"{qgis_profiles_path}"
            self.addCleanup(
                lambda: (
                    environ.__setitem__(
                        "QGIS_CUSTOM_CONFIG_PATH", initial_custom_config_path
                    )
                    if initial_custom_config_path is not None
                    else environ.pop("QGIS_CUSTOM_CONFIG_PATH", None)
                )
            )

            # downloaded profile, authored for QGIS 3
            downloaded_folder = Path(tmpdirname).joinpath("downloaded", "demo")
            downloaded_folder.joinpath("QGIS").mkdir(parents=True)
            downloaded_folder.joinpath("QGIS", "QGIS3.ini").write_text(
                "[qgis]\nfromProfileRepo=true\n", encoding="UTF8"
            )

            # installed profile, as created by QGIS 4
            installed_folder = qgis_profiles_path.joinpath("demo")
            installed_folder.joinpath("QGIS").mkdir(parents=True)
            installed_folder.joinpath("QGIS", "QGIS4.ini").write_text(
                "[qgis]\nsetByEndUser=true\n", encoding="UTF8"
            )

            downloaded_profile = QdtProfile(name="demo", folder=downloaded_folder)
            downloaded_profile.os_config.qgis_version_major = 4
            installed_profile = QdtProfile(name="demo", folder=installed_folder)
            installed_profile.os_config.qgis_version_major = 4

            downloaded_profile.merge_to(installed_profile)

            installed_ini_files = sorted(
                f.name for f in installed_folder.joinpath("QGIS").iterdir()
            )
            self.assertEqual(installed_ini_files, ["QGIS4.ini"])

            merged_content = installed_folder.joinpath("QGIS", "QGIS4.ini").read_text(
                encoding="UTF8"
            )
            # settings shipped by the profile and set by the end-user are both kept
            self.assertIn("fromProfileRepo", merged_content)
            self.assertIn("setByEndUser", merged_content)


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
