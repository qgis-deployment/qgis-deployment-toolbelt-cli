#! python3  # noqa E265

"""Usage from the repo root folder:

.. code-block:: python

    # for whole test
    python -m unittest tests.test_job_plugins_synchronizer
    # for specific
    python -m unittest tests.test_job_plugins_synchronizer.TestJobPluginsSynchronizer.test_install_plugin_upgrade_mode_delete
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import tempfile
import unittest
import zipfile
from pathlib import Path

# package
from qgis_deployment_toolbelt.jobs.job_plugins_synchronizer import (
    JobPluginsSynchronizer,
)
from qgis_deployment_toolbelt.plugins.plugin import QgisPlugin
from qgis_deployment_toolbelt.profiles.qdt_profile import QdtProfile


# #############################################################################
# ########## Classes ###############
# ##################################


class TestJobPluginsSynchronizer(unittest.TestCase):
    """Test plugins synchronizer job."""

    # -- Standard methods --------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """Executed when module is loaded before any test."""
        pass

    @classmethod
    def tearDownClass(cls):
        """Executed when module is unloaded after all tests."""
        pass

    # -- Helpers -----------------------------------------------------------------
    @staticmethod
    def _create_fake_plugin_zip(zip_path: Path, folder_name: str) -> None:
        """Create a minimal plugin zip archive with a metadata.txt."""
        with zipfile.ZipFile(zip_path, "w") as zf:
            zf.writestr(
                f"{folder_name}/metadata.txt",
                "[general]\nname=Test Plugin\nversion=2.0.0\n",
            )
            zf.writestr(f"{folder_name}/__init__.py", "")

    @staticmethod
    def _make_profile_in_tmpdir(tmp_dir: Path, name: str) -> QdtProfile:
        """Create a QdtProfile whose path_in_qgis points into the temp dir."""
        profile = QdtProfile(name=name)
        profile.os_config.qgis_profiles_path = tmp_dir / "qgis_profiles"
        return profile

    # -- Tests -------------------------------------------------------------------
    def test_install_plugin_upgrade_mode_delete(self):
        """Test that upgrade_mode=delete removes the plugin folder before unzip."""
        with tempfile.TemporaryDirectory(
            prefix="QDT_test_plugins_sync_upgrade_delete_"
        ) as tmp_dir:
            options = {"action": "create_or_restore"}
            job = JobPluginsSynchronizer(options=options)

            profile = self._make_profile_in_tmpdir(Path(tmp_dir), "test_delete")
            plugins_folder = profile.path_in_qgis / "python/plugins"
            plugin_folder = plugins_folder / "test_plugin"
            plugin_folder.mkdir(parents=True, exist_ok=True)

            # simulate an old installed plugin with a leftover file
            leftover_file = plugin_folder / "old_leftover.py"
            leftover_file.write_text("# this file should be removed")

            # create a fake plugin zip
            zip_path = Path(tmp_dir) / "test_plugin_delete.zip"
            self._create_fake_plugin_zip(zip_path, "test_plugin")

            # plugin object with upgrade_mode=delete
            plugin = QgisPlugin.from_dict(
                {
                    "name": "Test Plugin",
                    "folder_name": "test_plugin",
                    "version": "2.0.0",
                    "upgrade_mode": "delete",
                }
            )

            # run install
            job.install_plugin_into_profile([(profile, plugin, zip_path)])

            # the leftover file should be gone
            self.assertFalse(leftover_file.exists())
            # the plugin folder should exist with new files
            self.assertTrue(plugin_folder.is_dir())
            self.assertTrue((plugin_folder / "metadata.txt").exists())
            self.assertTrue((plugin_folder / "__init__.py").exists())

    def test_install_plugin_upgrade_mode_keep(self):
        """Test that upgrade_mode=keep preserves existing files in the plugin folder."""
        with tempfile.TemporaryDirectory(
            prefix="QDT_test_plugins_sync_upgrade_keep_"
        ) as tmp_dir:
            options = {"action": "create_or_restore"}
            job = JobPluginsSynchronizer(options=options)

            profile = self._make_profile_in_tmpdir(Path(tmp_dir), "test_keep")
            plugins_folder = profile.path_in_qgis / "python/plugins"
            plugin_folder = plugins_folder / "test_plugin"
            plugin_folder.mkdir(parents=True, exist_ok=True)

            # simulate an old installed plugin with a leftover file
            leftover_file = plugin_folder / "old_leftover.py"
            leftover_file.write_text("# this file should remain")

            # create a fake plugin zip
            zip_path = Path(tmp_dir) / "test_plugin_keep.zip"
            self._create_fake_plugin_zip(zip_path, "test_plugin")

            # plugin object with upgrade_mode=keep (default)
            plugin = QgisPlugin.from_dict(
                {
                    "name": "Test Plugin",
                    "folder_name": "test_plugin",
                    "version": "2.0.0",
                    "upgrade_mode": "keep",
                }
            )

            # run install
            job.install_plugin_into_profile([(profile, plugin, zip_path)])

            # the leftover file should still be there
            self.assertTrue(leftover_file.exists())
            # and the new files should also be present
            self.assertTrue((plugin_folder / "metadata.txt").exists())
            self.assertTrue((plugin_folder / "__init__.py").exists())


# #############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
