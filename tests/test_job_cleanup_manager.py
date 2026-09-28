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
from pathlib import Path
from unittest.mock import patch

# package
from qgis_deployment_toolbelt.constants import MANAGED_PLUGINS_MANIFEST_FILENAME
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
        profile_folder: Path, name: str, deprecated: bool | None = None
    ) -> Path:
        """Create a profile folder with a profile.json in it."""
        profile_folder.mkdir(parents=True, exist_ok=True)
        profile_data: dict = {"name": name, "version": "1.0.0"}
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

    def test_cleanup_profiles_deprecated(self):
        """Only installed profiles flagged as deprecated must be selected."""
        with tempfile.TemporaryDirectory(
            prefix="QDT_test_cleanup_profiles_deprecated_"
        ) as tmp_dir:
            qgis_profiles_path = Path(tmp_dir).joinpath("profiles").resolve()
            downloaded_path = Path(tmp_dir).joinpath("downloaded").resolve()

            # installed profiles
            deprecated_installed = self._make_installed_profile(
                qgis_profiles_path.joinpath("deprecated_installed"),
                name="deprecated_installed",
                deprecated=True,
            )
            regular_installed = self._make_installed_profile(
                qgis_profiles_path.joinpath("regular"), name="regular"
            )
            # installed profile deprecated in the downloaded copy only
            deprecated_remote_installed = qgis_profiles_path.joinpath(
                "deprecated_remote"
            )
            deprecated_remote_installed.mkdir(parents=True, exist_ok=True)

            # downloaded profiles
            self._make_installed_profile(
                downloaded_path.joinpath("repo/deprecated_remote"),
                name="deprecated_remote",
                deprecated=True,
            )
            # deprecated but never installed: nothing to remove
            self._make_installed_profile(
                downloaded_path.joinpath("repo/deprecated_never_installed"),
                name="deprecated_never_installed",
                deprecated=True,
            )

            job = JobCleanupManager(
                options={"dry_run": True, "scopes": ["profiles_deprecated"]}
            )
            job.qgis_profiles_path = qgis_profiles_path
            job.qdt_downloaded_repositories = downloaded_path

            report = job.run()

            self.assertIn(deprecated_installed, report.removed)
            self.assertIn(deprecated_remote_installed, report.removed)
            self.assertNotIn(regular_installed, report.removed)
            self.assertEqual(len(report.removed), 2)
            # dry-run: nothing has been actually removed
            self.assertTrue(deprecated_installed.is_dir())

    def test_cleanup_profiles_deprecated_stays_within_profiles_folder(self):
        """A profile name escaping the QGIS profiles folder must be ignored."""
        with tempfile.TemporaryDirectory(
            prefix="QDT_test_cleanup_profiles_traversal_"
        ) as tmp_dir:
            qgis_profiles_path = Path(tmp_dir).joinpath("profiles").resolve()
            qgis_profiles_path.mkdir(parents=True, exist_ok=True)
            downloaded_path = Path(tmp_dir).joinpath("downloaded").resolve()
            out_of_scope_folder = Path(tmp_dir).joinpath("outside").resolve()
            out_of_scope_folder.mkdir(parents=True, exist_ok=True)

            self._make_installed_profile(
                downloaded_path.joinpath("repo/evil"),
                name="../outside",
                deprecated=True,
            )

            job = JobCleanupManager(
                options={"dry_run": True, "scopes": ["profiles_deprecated"]}
            )
            job.qgis_profiles_path = qgis_profiles_path
            job.qdt_downloaded_repositories = downloaded_path

            report = job.run()

            self.assertEqual(report.removed, [])
            self.assertTrue(out_of_scope_folder.is_dir())
