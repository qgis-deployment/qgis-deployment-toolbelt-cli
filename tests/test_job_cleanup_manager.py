#! python3  # noqa E265

"""Usage from the repo root folder:

.. code-block:: python

    # for whole test
    python -m unittest tests.test_job_cleanup_manager
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import json
import tempfile
import unittest
from os import environ
from pathlib import Path
from unittest.mock import patch

# package
from qgis_deployment_toolbelt.constants import (
    ENV_VAR_QGIS_VERSION,
    MANAGED_PLUGINS_MANIFEST_FILENAME,
)
from qgis_deployment_toolbelt.jobs.job_cleanup_manager import JobCleanupManager
from qgis_deployment_toolbelt.profiles.qdt_profile import QdtProfile


# #############################################################################
# ########## Classes ###############
# ##################################


class TestJobCleanupManager(unittest.TestCase):
    """Test cleanup manager job."""

    @staticmethod
    def _make_profile(
        name: str, qgis_profiles_path: Path, plugins: list[dict]
    ) -> QdtProfile:
        """Create a profile object with deterministic installed path for tests."""
        profile = QdtProfile(name=name, plugins=plugins)
        profile.os_config.qgis_profiles_path = qgis_profiles_path
        return profile

    @staticmethod
    def _make_installed_profile(
        profile_folder: Path,
        name: str,
        deprecated: bool | None = None,
        **extra_attributes: str,
    ) -> Path:
        """Create a profile folder with a profile.json in it."""
        profile_folder.mkdir(parents=True, exist_ok=True)
        profile_data: dict = {"name": name, "version": "1.0.0", **extra_attributes}
        if deprecated is not None:
            profile_data["deprecated"] = deprecated
        profile_folder.joinpath("profile.json").write_text(
            json.dumps(profile_data), encoding="UTF-8"
        )
        return profile_folder

    def test_run_dispatches_scopes(self):
        """Run must dispatch cleanup methods according to requested scopes."""
        with patch.object(JobCleanupManager, "cleanup_plugins_cache") as mock_cache:
            with patch.object(
                JobCleanupManager, "cleanup_plugins_installed"
            ) as mock_installed:
                job = JobCleanupManager(options={"scopes": ["plugins_installed"]})
                job.run()
                mock_cache.assert_not_called()
                mock_installed.assert_called_once()

        with patch.object(JobCleanupManager, "cleanup_plugins_cache") as mock_cache:
            with patch.object(
                JobCleanupManager, "cleanup_plugins_installed"
            ) as mock_installed:
                job = JobCleanupManager(
                    options={"scopes": ["plugins_cache", "plugins_installed"]}
                )
                job.run()
                mock_cache.assert_called_once()
                mock_installed.assert_called_once()

    def test_cleanup_plugins_installed_removes_only_stale_managed(self):
        """Only stale plugins from QDT managed manifest should be selected."""
        with tempfile.TemporaryDirectory(
            prefix="QDT_test_cleanup_installed_"
        ) as tmp_dir:
            qgis_profiles_path = Path(tmp_dir) / "profiles"

            profile = self._make_profile(
                name="test_profile",
                qgis_profiles_path=qgis_profiles_path,
                plugins=[
                    {
                        "name": "Keep Plugin",
                        "version": "1.0.0",
                        "folder_name": "keep_plugin",
                    }
                ],
            )

            plugins_folder = profile.path_in_qgis / "python/plugins"
            keep_plugin_folder = plugins_folder / "keep_plugin"
            stale_plugin_folder = plugins_folder / "old_plugin"
            keep_plugin_folder.mkdir(parents=True, exist_ok=True)
            stale_plugin_folder.mkdir(parents=True, exist_ok=True)

            manifest_path = plugins_folder / MANAGED_PLUGINS_MANIFEST_FILENAME
            manifest_path.write_text(
                json.dumps(
                    {
                        "keep_plugin": {"plg_id": "keep"},
                        "old_plugin": {"plg_id": "old"},
                    }
                ),
                encoding="UTF-8",
            )

            job = JobCleanupManager(
                options={"dry_run": True, "scopes": ["plugins_installed"]}
            )

            with patch.object(
                JobCleanupManager,
                "list_installed_profiles",
                return_value=(profile,),
            ):
                with patch.object(
                    JobCleanupManager,
                    "list_downloaded_profiles",
                    return_value=(),
                ):
                    report = job.run()

            self.assertIn(stale_plugin_folder, report.removed)
            self.assertNotIn(keep_plugin_folder, report.removed)

    def _run_profiles_deprecated(self, tmp_dir: str) -> list[Path]:
        """Run the job in dry-run mode on the 'profiles_deprecated' scope only."""
        job = JobCleanupManager(
            options={"dry_run": True, "scopes": ["profiles_deprecated"]}
        )
        job.qgis_profiles_path = Path(tmp_dir, "profiles")
        job.qdt_downloaded_repositories = Path(tmp_dir, "downloaded")
        return job.run().removed

    def test_cleanup_profiles_deprecated(self):
        """Only installed profiles deprecated in the downloaded repositories are
        selected, and nothing is removed in dry-run mode."""
        with tempfile.TemporaryDirectory(prefix="QDT_test_cleanup_") as tmp_dir:
            profiles = Path(tmp_dir, "profiles")
            downloaded = Path(tmp_dir, "downloaded/repo")
            for name, deprecated in (("old", True), ("kept", None), ("gone", True)):
                self._make_installed_profile(downloaded / name, name, deprecated)
            # installed copies never carry the flag: deprecated ones aren't synced
            for name in ("old", "kept", "manual"):
                self._make_installed_profile(profiles / name, name)

            removed = self._run_profiles_deprecated(tmp_dir)

            self.assertEqual(removed, [profiles / "old"])
            self.assertTrue(profiles.joinpath("old").is_dir())

    def test_cleanup_profiles_deprecated_keeps_profile_active_elsewhere(self):
        """A profile deprecated in a repository but active in another one is kept."""
        with tempfile.TemporaryDirectory(prefix="QDT_test_cleanup_") as tmp_dir:
            downloaded = Path(tmp_dir, "downloaded")
            self._make_installed_profile(Path(tmp_dir, "profiles/dup"), "dup")
            self._make_installed_profile(downloaded / "repo_a/dup", "dup", True)
            self._make_installed_profile(downloaded / "repo_b/dup", "dup", False)

            self.assertEqual(self._run_profiles_deprecated(tmp_dir), [])

    def test_cleanup_profiles_deprecated_ignores_profile_not_deployed_by_qdt(self):
        """An installed folder without profile.json (typically created from QGIS) is kept,
        even if its name matches a deprecated profile."""
        with tempfile.TemporaryDirectory(prefix="QDT_test_cleanup_") as tmp_dir:
            self._make_installed_profile(
                Path(tmp_dir, "downloaded/repo/old"), "old", True
            )
            manual = Path(tmp_dir, "profiles/old")
            manual.mkdir(parents=True)

            self.assertEqual(self._run_profiles_deprecated(tmp_dir), [])
            self.assertTrue(manual.is_dir())

    def test_cleanup_profiles_deprecated_stays_within_profiles_folder(self):
        """A profile name escaping the QGIS profiles folder must be ignored."""
        with tempfile.TemporaryDirectory(prefix="QDT_test_cleanup_") as tmp_dir:
            Path(tmp_dir, "profiles").mkdir()
            outside = Path(tmp_dir, "outside")
            outside.mkdir()
            self._make_installed_profile(
                Path(tmp_dir, "downloaded/repo/evil"), "../outside", True
            )

            self.assertEqual(self._run_profiles_deprecated(tmp_dir), [])
            self.assertTrue(outside.is_dir())

    def _run_profiles_incompatible_qgis(
        self, tmp_dir: str, qgis_version: str | None
    ) -> list[Path]:
        """Run the job in dry-run mode on the 'profiles_incompatible_qgis' scope only,
        targeting the given QGIS version (unset if None)."""
        with patch.dict(environ):
            environ.pop(ENV_VAR_QGIS_VERSION, None)
            if qgis_version:
                environ[ENV_VAR_QGIS_VERSION] = qgis_version
            job = JobCleanupManager(
                options={"dry_run": True, "scopes": ["profiles_incompatible_qgis"]}
            )
            job.qgis_profiles_path = Path(tmp_dir, "profiles")
            job.qdt_downloaded_repositories = Path(tmp_dir, "downloaded")
            return job.run().removed

    def test_cleanup_profiles_incompatible_qgis(self):
        """Only installed profiles whose downloaded version excludes the targeted QGIS
        version are selected, and nothing is removed in dry-run mode."""
        with tempfile.TemporaryDirectory(prefix="QDT_test_cleanup_") as tmp_dir:
            profiles = Path(tmp_dir, "profiles")
            downloaded = Path(tmp_dir, "downloaded/repo")
            for name, bounds in (
                ("too_old", {"qgisMaximumVersion": "3.34.99"}),
                ("too_new", {"qgisMinimumVersion": "4.0.0"}),
                ("in_bounds", {"qgisMinimumVersion": "3.40.0"}),
                ("no_bounds", {}),
                ("not_installed", {"qgisMaximumVersion": "3.34.99"}),
            ):
                self._make_installed_profile(downloaded / name, name, **bounds)
            for name in ("too_old", "too_new", "in_bounds", "no_bounds", "manual"):
                self._make_installed_profile(profiles / name, name)

            removed = self._run_profiles_incompatible_qgis(tmp_dir, "3.40.5")

            self.assertEqual(
                sorted(removed), [profiles / "too_new", profiles / "too_old"]
            )
            self.assertTrue(profiles.joinpath("too_old").is_dir())

    def test_cleanup_profiles_incompatible_qgis_keeps_profile_compatible_elsewhere(
        self,
    ):
        """A profile incompatible in a repository but compatible in another one is
        kept."""
        with tempfile.TemporaryDirectory(prefix="QDT_test_cleanup_") as tmp_dir:
            downloaded = Path(tmp_dir, "downloaded")
            self._make_installed_profile(Path(tmp_dir, "profiles/dup"), "dup")
            self._make_installed_profile(
                downloaded / "repo_a/dup", "dup", qgisMaximumVersion="3.34.99"
            )
            self._make_installed_profile(
                downloaded / "repo_b/dup", "dup", qgisMaximumVersion="3.40.99"
            )

            self.assertEqual(
                self._run_profiles_incompatible_qgis(tmp_dir, "3.40.5"), []
            )

    def test_cleanup_profiles_incompatible_qgis_without_targeted_version(self):
        """Nothing is removed when the targeted QGIS version is unknown."""
        with tempfile.TemporaryDirectory(prefix="QDT_test_cleanup_") as tmp_dir:
            self._make_installed_profile(Path(tmp_dir, "profiles/old"), "old")
            self._make_installed_profile(
                Path(tmp_dir, "downloaded/repo/old"), "old", qgisMaximumVersion="3.0.0"
            )

            self.assertEqual(self._run_profiles_incompatible_qgis(tmp_dir, None), [])
