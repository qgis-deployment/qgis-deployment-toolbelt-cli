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
