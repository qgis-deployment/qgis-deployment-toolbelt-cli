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
import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

# package
from qgis_deployment_toolbelt.constants import MANAGED_PLUGINS_MANIFEST_FILENAME
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

    # -- QDT-managed plugins manifest --------------------------------------------
    def test_read_qdt_managed_plugins_manifest_missing_file_returns_empty(self):
        """Test that reading a non-existing manifest returns an empty dict."""
        with tempfile.TemporaryDirectory(
            prefix="QDT_test_plugins_sync_manifest_read_missing_"
        ) as tmp_dir:
            job = JobPluginsSynchronizer(options={"action": "create_or_restore"})

            manifest_path = Path(tmp_dir) / MANAGED_PLUGINS_MANIFEST_FILENAME
            self.assertFalse(manifest_path.exists())

            manifest = job._read_qdt_managed_plugins_manifest(
                manifest_path=manifest_path
            )
            self.assertEqual(manifest, {})

    def test_read_qdt_managed_plugins_manifest_corrupted_file_returns_empty(self):
        """Test that reading a corrupted manifest logs a warning and returns an
        empty dict instead of raising."""
        with tempfile.TemporaryDirectory(
            prefix="QDT_test_plugins_sync_manifest_read_corrupted_"
        ) as tmp_dir:
            job = JobPluginsSynchronizer(options={"action": "create_or_restore"})

            manifest_path = Path(tmp_dir) / MANAGED_PLUGINS_MANIFEST_FILENAME
            manifest_path.write_text("this is not valid json", encoding="UTF-8")

            manifest = job._read_qdt_managed_plugins_manifest(
                manifest_path=manifest_path
            )
            self.assertEqual(manifest, {})

    def test_read_qdt_managed_plugins_manifest_existing_file(self):
        """Test that reading an existing valid manifest returns its content."""
        with tempfile.TemporaryDirectory(
            prefix="QDT_test_plugins_sync_manifest_read_existing_"
        ) as tmp_dir:
            job = JobPluginsSynchronizer(options={"action": "create_or_restore"})

            manifest_path = Path(tmp_dir) / MANAGED_PLUGINS_MANIFEST_FILENAME
            manifest_path.write_text(
                json.dumps({"test_plugin": {"plg_version": "1.0.0"}}),
                encoding="UTF-8",
            )

            manifest = job._read_qdt_managed_plugins_manifest(
                manifest_path=manifest_path
            )
            self.assertEqual(manifest["test_plugin"]["plg_version"], "1.0.0")

    def test_add_plugin_to_manifest_creates_entry(self):
        """Test that a plugin entry is added to an empty manifest dict, in memory."""
        job = JobPluginsSynchronizer(options={"action": "create_or_restore"})

        plugin = QgisPlugin.from_dict(
            {
                "name": "Test Plugin",
                "folder_name": "test_plugin",
                "version": "2.0.0",
                "plugin_id": 42,
            }
        )

        manifest: dict = {}
        job._add_plugin_to_manifest(manifest=manifest, plugin=plugin)

        self.assertIn("test_plugin", manifest)
        self.assertEqual(manifest["test_plugin"]["plg_version"], "2.0.0")
        self.assertEqual(manifest["test_plugin"]["plg_id"], "42")
        self.assertIn("installed_at", manifest["test_plugin"])
        self.assertIn("qdt_version", manifest["test_plugin"])

    def test_add_plugin_to_manifest_updates_existing_entry_preserving_others(self):
        """Test that adding a plugin updates its own entry in place while
        preserving other existing entries in the same manifest dict."""
        job = JobPluginsSynchronizer(options={"action": "create_or_restore"})

        other_plugin = QgisPlugin.from_dict(
            {"name": "Other Plugin", "folder_name": "other_plugin", "version": "1.0.0"}
        )
        plugin_v1 = QgisPlugin.from_dict(
            {"name": "Test Plugin", "folder_name": "test_plugin", "version": "1.0.0"}
        )
        plugin_v2 = QgisPlugin.from_dict(
            {"name": "Test Plugin", "folder_name": "test_plugin", "version": "2.0.0"}
        )

        manifest: dict = {}
        job._add_plugin_to_manifest(manifest=manifest, plugin=other_plugin)
        job._add_plugin_to_manifest(manifest=manifest, plugin=plugin_v1)
        job._add_plugin_to_manifest(manifest=manifest, plugin=plugin_v2)

        self.assertEqual(len(manifest), 2)
        self.assertEqual(manifest["other_plugin"]["plg_version"], "1.0.0")
        self.assertEqual(manifest["test_plugin"]["plg_version"], "2.0.0")

    def test_write_qdt_managed_plugins_manifest(self):
        """Test that the manifest dict is correctly serialized to disk as JSON."""
        with tempfile.TemporaryDirectory(
            prefix="QDT_test_plugins_sync_manifest_write_"
        ) as tmp_dir:
            job = JobPluginsSynchronizer(options={"action": "create_or_restore"})

            manifest_path = Path(tmp_dir) / MANAGED_PLUGINS_MANIFEST_FILENAME
            job._write_qdt_managed_plugins_manifest(
                manifest_path=manifest_path,
                manifest={"test_plugin": {"plg_version": "2.0.0"}},
            )

            self.assertTrue(manifest_path.is_file())
            written = json.loads(manifest_path.read_text(encoding="UTF-8"))
            self.assertEqual(written["test_plugin"]["plg_version"], "2.0.0")

    def test_install_plugin_into_profile_writes_manifest(self):
        """Test that installing a plugin also records it into the QDT managed
        plugins manifest, with the expected fields."""
        with tempfile.TemporaryDirectory(
            prefix="QDT_test_plugins_sync_install_manifest_"
        ) as tmp_dir:
            options = {"action": "create_or_restore"}
            job = JobPluginsSynchronizer(options=options)

            profile = self._make_profile_in_tmpdir(Path(tmp_dir), "test_manifest")
            plugins_folder = profile.path_in_qgis / "python/plugins"

            zip_path = Path(tmp_dir) / "test_plugin_manifest.zip"
            self._create_fake_plugin_zip(zip_path, "test_plugin")

            plugin = QgisPlugin.from_dict(
                {
                    "name": "Test Plugin",
                    "folder_name": "test_plugin",
                    "version": "2.0.0",
                    "plugin_id": 42,
                }
            )

            job.install_plugin_into_profile([(profile, plugin, zip_path)])

            manifest_path = plugins_folder / MANAGED_PLUGINS_MANIFEST_FILENAME
            self.assertTrue(manifest_path.is_file())

            manifest = json.loads(manifest_path.read_text(encoding="UTF-8"))
            self.assertIn("test_plugin", manifest)
            self.assertEqual(manifest["test_plugin"]["plg_version"], "2.0.0")
            self.assertEqual(manifest["test_plugin"]["plg_id"], "42")

    def test_install_plugin_into_profile_writes_manifest_once_for_several_plugins(
        self,
    ):
        """Test that the manifest is read and written only once per profile, no
        matter how many plugins are installed into it in a single call."""
        with tempfile.TemporaryDirectory(
            prefix="QDT_test_plugins_sync_install_manifest_batch_"
        ) as tmp_dir:
            options = {"action": "create_or_restore"}
            job = JobPluginsSynchronizer(options=options)

            profile = self._make_profile_in_tmpdir(Path(tmp_dir), "test_batch")
            plugins_folder = profile.path_in_qgis / "python/plugins"

            zip_path_one = Path(tmp_dir) / "plugin_one.zip"
            self._create_fake_plugin_zip(zip_path_one, "plugin_one")
            zip_path_two = Path(tmp_dir) / "plugin_two.zip"
            self._create_fake_plugin_zip(zip_path_two, "plugin_two")

            plugin_one = QgisPlugin.from_dict(
                {"name": "Plugin One", "folder_name": "plugin_one", "version": "1.0.0"}
            )
            plugin_two = QgisPlugin.from_dict(
                {"name": "Plugin Two", "folder_name": "plugin_two", "version": "1.0.0"}
            )

            with patch.object(
                job,
                "_write_qdt_managed_plugins_manifest",
                wraps=job._write_qdt_managed_plugins_manifest,
            ) as mock_write:
                job.install_plugin_into_profile(
                    [
                        (profile, plugin_one, zip_path_one),
                        (profile, plugin_two, zip_path_two),
                    ]
                )
                # a single write for the two plugins installed into the same profile
                self.assertEqual(mock_write.call_count, 1)

            # both plugins must still be present in the resulting manifest
            manifest_path = plugins_folder / MANAGED_PLUGINS_MANIFEST_FILENAME
            manifest = json.loads(manifest_path.read_text(encoding="UTF-8"))
            self.assertIn("plugin_one", manifest)
            self.assertIn("plugin_two", manifest)


# #############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
