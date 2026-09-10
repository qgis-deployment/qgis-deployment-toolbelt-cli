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


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
