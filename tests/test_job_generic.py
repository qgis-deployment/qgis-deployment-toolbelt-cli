#! python3  # noqa E265

"""Usage from the repo root folder:

.. code-block:: python

    # for whole test
    python -m unittest tests.test_job_generic
    # for specific
    python -m unittest tests.test_job_generic.TestJobGeneric.test_listing_profiles_folder
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

# package
from qgis_deployment_toolbelt.exceptions import (
    JobOptionBadNameError,
    JobOptionBadValueError,
    JobOptionBadValueTypeError,
)
from qgis_deployment_toolbelt.jobs.generic_job import GenericJob
from qgis_deployment_toolbelt.profiles.qdt_profile import QdtProfile


# #############################################################################
# ########## Classes ###############
# ##################################


class JobFixture(GenericJob):
    """Minimal concrete job used to test the abstract base class."""

    ID: str = "job-test-fixture"
    OPTIONS_SCHEMA: dict = {
        "option_one": {
            "type": str,
            "required": True,
            "default": "git",
            "condition": "startswith",
            "possible_values": ("git", "http"),
        },
        "option_two": {
            "type": (bool, int, str),
            "required": False,
            "condition": "in",
            "possible_values": ("test", "fixture"),
        },
        "option_three": {
            "type": (bool, int, str),
            "required": False,
            "condition": None,
            "possible_values": None,
        },
        "option_four": {
            "type": list,
            "required": False,
            "condition": "all_in",
            "possible_values": ("plugins_cache", "plugins_installed"),
        },
    }

    def run(self) -> None:
        """No-op implementation of the abstract method."""


class TestJobGeneric(unittest.TestCase):
    """Test generic job."""

    # -- Standard methods --------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """Executed when module is loaded before any test."""
        cls.generic_job = JobFixture()

    # -- TESTS ---------------------------------------------------------
    def test_generic_job_is_abstract(self):
        """GenericJob and incomplete subclasses cannot be instantiated."""

        # rebinding the abstract member drops the implementation from JobFixture
        class JobWithoutId(JobFixture):
            ID = GenericJob.ID

        class JobWithoutOptionsSchema(JobFixture):
            OPTIONS_SCHEMA = GenericJob.OPTIONS_SCHEMA

        class JobWithoutRun(JobFixture):
            run = GenericJob.run

        for job_class in (
            GenericJob,
            JobWithoutId,
            JobWithoutOptionsSchema,
            JobWithoutRun,
        ):
            with self.subTest(job=job_class.__name__), self.assertRaises(TypeError):
                job_class()

    def test_abstract_members_raise_when_called(self):
        """Abstract members fail loudly when reached through super()."""
        for member in (
            GenericJob.ID.fget,
            GenericJob.OPTIONS_SCHEMA.fget,
            GenericJob.run,
        ):
            with (
                self.subTest(member=member.__name__),
                self.assertRaises(NotImplementedError),
            ):
                member(self.generic_job)

    def test_listing_profiles_folder(self):
        """Test profiles listing."""
        fixtures_profiles_folder = Path("tests/fixtures/profiles")
        with tempfile.TemporaryDirectory(
            prefix="QDT_test_profiles_listing_",
            ignore_cleanup_errors=True,
        ) as tmpdirname:
            tmp_folder_path = Path(tmpdirname).joinpath("profiles")
            # simulate a QGIS profiles folder structure in the temp folder
            for p in fixtures_profiles_folder.glob("good_profile_*.json"):
                dest_file = tmp_folder_path.joinpath(f"test_{p.stem}/profile.json")
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                dest_file.write_text(p.read_text(encoding="UTF-8"), encoding="UTF-8")

            filtered_profiles = self.generic_job.filter_profiles_folder(
                start_parent_folder=tmp_folder_path
            )

            self.assertIsInstance(filtered_profiles, tuple)
            self.assertGreater(len(filtered_profiles), 0)

            # length must be -2 because of a profile which is excluded by a rule
            # and another one which is flagged as deprecated
            self.assertEqual(
                len(filtered_profiles),
                len(list(tmp_folder_path.glob("**/profile.json"))) - 2,
            )

    def test_listing_profiles_folder_excludes_incompatible_qdt_version(self):
        """Profiles whose qdtMinVersion is not satisfied must be filtered out."""
        fixtures_profiles_folder = Path("tests/fixtures/profiles")
        with tempfile.TemporaryDirectory(
            prefix="QDT_test_profiles_qdt_min_version_",
            ignore_cleanup_errors=True,
        ) as tmpdirname:
            tmp_folder_path = Path(tmpdirname).joinpath("profiles")
            for p in fixtures_profiles_folder.glob("*_profile_qdt_min_version_*.json"):
                dest_file = tmp_folder_path.joinpath(f"test_{p.stem}/profile.json")
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                dest_file.write_text(p.read_text(encoding="UTF-8"), encoding="UTF-8")

            filtered_profiles = self.generic_job.filter_profiles_folder(
                start_parent_folder=tmp_folder_path
            )

            self.assertIsInstance(filtered_profiles, tuple)
            filtered_names = [p.name for p in filtered_profiles]
            self.assertIn("qdt_test_profile_qdt_min_version_satisfied", filtered_names)
            self.assertNotIn(
                "qdt_test_profile_qdt_min_version_too_high", filtered_names
            )
            self.assertIn("qdt_test_profile_qdt_min_version_invalid", filtered_names)

    # -- rules verdicts cache ------------------------------------------------
    ALWAYS_MATCHING_RULES: list[dict] = [
        {
            "name": "Always",
            "conditions": {
                "all": [
                    {
                        "path": "$.date.current_year",
                        "value": 1985,
                        "operator": "not_equal",
                    }
                ]
            },
        }
    ]
    NEVER_MATCHING_RULES: list[dict] = [
        {
            "name": "Never",
            "conditions": {
                "all": [
                    {"path": "$.date.current_year", "value": 1985, "operator": "equal"}
                ]
            },
        }
    ]

    @staticmethod
    def _write_profile(folder: Path, version: str, rules: list | None) -> None:
        """Write a minimal profile.json into the given folder."""
        folder.mkdir(parents=True, exist_ok=True)
        content = {"name": folder.name, "version": version}
        if rules is not None:
            content["rules"] = rules
        folder.joinpath("profile.json").write_text(
            json.dumps(content), encoding="UTF-8"
        )

    def test_rescan_returns_updated_profiles_with_same_rules(self):
        """After a profile update on disk and a cache clearing, a re-scan must
        return the updated profile objects, even if their rules did not change."""
        with (
            patch.dict(GenericJob.RULES_FILTER_CACHE, clear=True),
            patch.dict(GenericJob.PROFILES_FOLDER_CACHE, clear=True),
            tempfile.TemporaryDirectory(prefix="QDT_test_rules_cache_") as tmp_dir,
        ):
            profiles_folder = Path(tmp_dir, "profiles")
            rules = self.ALWAYS_MATCHING_RULES
            self._write_profile(profiles_folder / "demo", "1.0.0", rules)
            first = self.generic_job.filter_profiles_folder(profiles_folder)
            self.assertEqual(first[0].version, "1.0.0")

            # simulate an update by another job, e.g. qprofiles-synchronizer
            self._write_profile(profiles_folder / "demo", "2.0.0", rules)
            GenericJob.clear_profiles_cache(folder_path=profiles_folder)

            second = self.generic_job.filter_profiles_folder(profiles_folder)
            self.assertEqual(second[0].version, "2.0.0")

    def test_rescan_evaluates_updated_rules(self):
        """Rules updated on disk must be evaluated again, not served from cache."""
        with (
            patch.dict(GenericJob.RULES_FILTER_CACHE, clear=True),
            patch.dict(GenericJob.PROFILES_FOLDER_CACHE, clear=True),
            tempfile.TemporaryDirectory(prefix="QDT_test_rules_cache_") as tmp_dir,
        ):
            profiles_folder = Path(tmp_dir, "profiles")
            self._write_profile(
                profiles_folder / "demo",
                "1.0.0",
                self.ALWAYS_MATCHING_RULES,
            )
            self.assertEqual(
                len(self.generic_job.filter_profiles_folder(profiles_folder)), 1
            )

            self._write_profile(
                profiles_folder / "demo", "2.0.0", self.NEVER_MATCHING_RULES
            )
            GenericJob.clear_profiles_cache(folder_path=profiles_folder)

            self.assertIsNone(self.generic_job.filter_profiles_folder(profiles_folder))

    def test_rules_evaluation_error_is_logged_and_profile_ignored(self):
        """A profile whose rules can't be evaluated is in none of the lists, the
        error details are logged once and the profile is reported as ignored each
        time, including when the result comes from the cache."""
        broken = QdtProfile(name="broken", rules=[{"name": "no conditions"}])
        with patch.dict(GenericJob.RULES_FILTER_CACHE, clear=True):
            for attempt in ("evaluated", "cached"):
                with (
                    self.subTest(attempt=attempt),
                    self.assertLogs("qgis_deployment_toolbelt", "WARNING") as logs,
                ):
                    matched, unmatched = self.generic_job.filter_profiles_on_rules(
                        (broken,)
                    )

                self.assertEqual((matched, unmatched), ([], []))
                errors = [r for r in logs.records if r.levelname == "ERROR"]
                warnings = [r for r in logs.records if r.levelname == "WARNING"]
                self.assertEqual(len(warnings), 1)
                self.assertIn("'broken' is ignored", warnings[0].getMessage())
                if attempt == "evaluated":
                    self.assertEqual(len(errors), 1)
                    # detail from the rule engine validation error
                    self.assertIn("conditions", errors[0].getMessage())
                else:
                    self.assertEqual(errors, [])

    def test_rules_verdict_is_reused(self):
        """Identical rules are evaluated only once, whatever the profiles."""
        profiles = tuple(
            QdtProfile(name=name, rules=self.NEVER_MATCHING_RULES)
            for name in ("one", "two")
        )
        with (
            patch.dict(GenericJob.RULES_FILTER_CACHE, clear=True),
            patch.object(
                GenericJob,
                "_evaluate_profile_rules",
                autospec=True,
                return_value=False,
            ) as mock_evaluate,
        ):
            matched, unmatched = self.generic_job.filter_profiles_on_rules(profiles)
            self.generic_job.filter_profiles_on_rules(profiles)

            mock_evaluate.assert_called_once()
            self.assertEqual(matched, [])
            self.assertEqual([p.name for p in unmatched], ["one", "two"])

            self.generic_job.filter_profiles_on_rules(profiles, cached=False)
            self.assertEqual(mock_evaluate.call_count, 3)

    def test_listing_profiles_folder_excludes_deprecated(self):
        """Profiles flagged as deprecated must be filtered out of the deployment,
        but still listed by a raw read."""
        fixtures_profiles_folder = Path("tests/fixtures/profiles")
        with tempfile.TemporaryDirectory(
            prefix="QDT_test_profiles_deprecated_",
            ignore_cleanup_errors=True,
        ) as tmpdirname:
            tmp_folder_path = Path(tmpdirname).joinpath("profiles")
            for p in (
                fixtures_profiles_folder.joinpath("good_profile_minimal.json"),
                fixtures_profiles_folder.joinpath("good_profile_deprecated.json"),
            ):
                dest_file = tmp_folder_path.joinpath(f"test_{p.stem}/profile.json")
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                dest_file.write_text(p.read_text(encoding="UTF-8"), encoding="UTF-8")

            filtered_profiles = self.generic_job.filter_profiles_folder(
                start_parent_folder=tmp_folder_path
            )

            self.assertIsInstance(filtered_profiles, tuple)
            filtered_names = [p.name for p in filtered_profiles]
            self.assertIn("qdt_test_profile_minimal", filtered_names)
            self.assertNotIn("qdt_test_profile_deprecated", filtered_names)

            # a raw read must still list them, so cleanup jobs can handle them
            all_names = [
                p.name
                for p in self.generic_job.read_profiles_folder(
                    start_parent_folder=tmp_folder_path
                )
            ]
            self.assertIn("qdt_test_profile_minimal", all_names)
            self.assertIn("qdt_test_profile_deprecated", all_names)

    def test_get_matching_profile_from_name(self):
        """Test get_matching_profile_from_name method."""
        fixtures_profiles_folder = Path("tests/fixtures/profiles")
        with tempfile.TemporaryDirectory(
            prefix="QDT_test_get_matching_profile_",
            ignore_cleanup_errors=True,
        ) as tmpdirname:
            tmp_folder_path = Path(tmpdirname).joinpath("profiles")
            # simulate a QGIS profiles folder structure in the temp folder
            for p in fixtures_profiles_folder.glob("good_profile_*.json"):
                dest_file = tmp_folder_path.joinpath(f"test_{p.stem}/profile.json")
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                dest_file.write_text(p.read_text(encoding="UTF-8"), encoding="UTF-8")

            filtered_profiles = self.generic_job.filter_profiles_folder(
                start_parent_folder=tmp_folder_path
            )
            matching_profile = self.generic_job.get_matching_profile_from_name(
                filtered_profiles, "qdt_test_profile_minimal"
            )
            self.assertIsInstance(matching_profile, QdtProfile)

            matching_profile = self.generic_job.get_matching_profile_from_name(
                filtered_profiles, "qdt_test_profile_minimal_not_found"
            )
            self.assertIsNone(matching_profile)

    def test_validate_options_bad_input_type(self):
        """Test validate_options method"""

        # Options must be a dictionary
        with self.assertRaises(TypeError):
            self.generic_job.validate_options(options="options_test")
        with self.assertRaises(TypeError):
            self.generic_job.validate_options(options=["options_test"])

    def test_validate_options_bad_name(self):
        """Test validate_options method"""
        # bad option name
        bad_option_name = {
            "option_one": "http://fake.url",
            "option_two": "test",
            "bad_option_name": "git",
        }

        with self.assertRaises(JobOptionBadNameError):
            self.generic_job.validate_options(bad_option_name)

    def test_validate_options_bad_condition_in(self):
        """Test validate_options method"""
        # bad value condition
        bad_options_scope = {
            "option_one": "https://fake.url",
            "option_two": "bad-value-not-in-possibles",
        }

        with self.assertRaises(JobOptionBadValueError):
            self.generic_job.validate_options(bad_options_scope)

    def test_validate_options_bad_condition_startswith(self):
        """Test validate_options method"""
        # bad value condition
        bad_options_scope = {
            "option_one": "bad-startswith",
            "option_two": "user",
        }

        with self.assertRaises(JobOptionBadValueError):
            self.generic_job.validate_options(bad_options_scope)

    def test_validate_options_bad_type(self):
        """Test validate_options method"""
        # bad value type
        bad_options = {
            "option_one": True,
            "option_two": "user",
        }

        with self.assertRaises(JobOptionBadValueTypeError):
            self.generic_job.validate_options(bad_options)

    def test_validate_options_bad_condition_all_in(self):
        """Test validate_options method with list values bound to a closed set."""
        bad_options_scope = {
            "option_one": "https://blog.geotribu.net",
            "option_four": ["plugins_cache", "wrong_scope"],
        }

        with self.assertRaises(JobOptionBadValueError):
            self.generic_job.validate_options(bad_options_scope)
