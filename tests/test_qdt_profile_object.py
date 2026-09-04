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
import unittest
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


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
