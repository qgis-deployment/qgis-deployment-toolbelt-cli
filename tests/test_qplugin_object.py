#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_qplugin_object
    # for specific test
    python -m unittest tests.test_qplugin_object.TestQgisPluginObject.test_profile_load_from_json_basic
"""

# standard
import unittest
from pathlib import Path
from shutil import rmtree

# project
from qgis_deployment_toolbelt.plugins.plugin import QgisPlugin
from qgis_deployment_toolbelt.profiles.qdt_profile import QdtProfile
from qgis_deployment_toolbelt.utils.file_downloader import download_remote_file_to_local


# ############################################################################
# ########## Classes #############
# ################################


class TestQgisPluginObject(unittest.TestCase):
    """Test QGIS Plugin abstraction class."""

    # -- Standard methods --------------------------------------------------------
    @classmethod
    def setUpClass(cls):
        """Executed when module is loaded before any test."""
        cls.good_profiles_files = sorted(
            Path("tests/fixtures/").glob("profiles/good_*.json")
        )

        # -- Download a plugin to perfom tests
        # prepare local download path
        cls.sample_plugin_downloaded = Path(
            "tests/fixtures/tmp/qtribu/2733_qtribu_0-14-2.zip"
        )
        cls.sample_plugin_downloaded.parent.mkdir(parents=True, exist_ok=True)

        # download plugin zip archive (only if it doesn't exist already)
        if not cls.sample_plugin_downloaded.exists():
            download_remote_file_to_local(
                remote_url_to_download="https://github.com/geotribu/qtribu/releases/download/0.14.2/qtribu.0.14.2.zip",
                local_file_path=cls.sample_plugin_downloaded.resolve(),
                content_type="application/zip",
            )

        # check download worked
        assert cls.sample_plugin_downloaded.is_file() is True, (
            "Downloading fixture plugin failed."
        )

    @classmethod
    def tearDownClass(cls) -> None:
        rmtree(path=cls.sample_plugin_downloaded.parent, ignore_errors=True)

    def test_qplugin_load_from_profile(self):
        """Test plugin object loading from profile object."""
        for p in self.good_profiles_files:
            qdt_profile = QdtProfile.from_json(
                profile_json_path=p,
                profile_folder=p.parent,
            )

            self.assertIsInstance(qdt_profile.plugins, list)
            if len(qdt_profile.plugins):
                for i in qdt_profile.plugins:
                    self.assertIsInstance(i, QgisPlugin)

    def test_qplugin_load_from_dict(self):
        """Test plugin object loading from JSON."""
        sample_plugin_complete = {
            "name": "french_locator_filter",
            "version": "1.0.4",
            "url": "https://plugins.qgis.org/plugins/french_locator_filter/version/1.0.4/download/",
            "location": "remote",
        }

        plugin_obj_one: QgisPlugin = QgisPlugin.from_dict(sample_plugin_complete)

        sample_plugin_incomplete = {
            "name": "french_locator_filter",
            "version": "1.0.4",
            "official_repository": True,
        }

        plugin_obj_two: QgisPlugin = QgisPlugin.from_dict(sample_plugin_incomplete)

        self.assertEqual(plugin_obj_one, plugin_obj_two)
        self.assertEqual(plugin_obj_one.download_url, plugin_obj_one.uri_to_zip)

    def test_qplugin_load_from_dict_local(self):
        """Test plugin object loading from dict, pointing to a local plugin."""
        # plugin as dict
        plugin_dict_local = {
            "name": "QTribu",
            "folder_name": "qtribu",
            "official_repository": False,
            "plugin_id": 2733,
            "location": "local",
            "url": self.sample_plugin_downloaded,
            "version": "0.14.2",
        }

        # plugin as object
        plugin_obj: QgisPlugin = QgisPlugin.from_dict(plugin_dict_local)
        self.assertIsInstance(plugin_obj.uri_to_zip, Path)

        # using a file:// prefix
        plugin_dict_local["url"] = f"file://{self.sample_plugin_downloaded}"
        plugin_obj: QgisPlugin = QgisPlugin.from_dict(plugin_dict_local)

    def test_qplugin_load_from_zip(self):
        """Test plugin object loading from a ZIP archive downloaded."""
        # plugin as dict
        sample_plugin_complex = {
            "name": "Layers menu from project",
            "version": "2.1.0",
            "url": "https://plugins.qgis.org/plugins/menu_from_project/version/2.1.0/download/",
            "location": "remote",
            "plugin_id": 1846,
        }
        # plugin as object
        plugin_obj: QgisPlugin = QgisPlugin.from_dict(sample_plugin_complex)

        # some attributes are not set
        self.assertIsNone(plugin_obj.folder_name)

        # prepare local download path
        local_plugin_download = Path(
            f"{self.sample_plugin_downloaded.parent.parent}/{plugin_obj.installation_folder_name}/"
            f"{plugin_obj.id_with_version}.zip"
        )

        # some attributes have been set
        self.assertIsNotNone(plugin_obj.folder_name)

        # download plugin zip archive
        download_remote_file_to_local(
            remote_url_to_download=plugin_obj.download_url,
            local_file_path=local_plugin_download.resolve(),
            content_type="application/zip",
        )

        # check download worked
        self.assertTrue(local_plugin_download.is_file())

        # load from zip
        plugin_obj_from_zip: QgisPlugin = QgisPlugin.from_zip(
            input_zip_path=local_plugin_download
        )

        # check types
        self.assertIsInstance(plugin_obj_from_zip.name, str)
        self.assertIsInstance(plugin_obj_from_zip.version, str)
        self.assertIsInstance(plugin_obj_from_zip.folder_name, str)
        self.assertIsInstance(plugin_obj_from_zip.qgis_maximum_version, str)
        self.assertIsInstance(plugin_obj_from_zip.qgis_minimum_version, str)

        # check values
        self.assertEqual(plugin_obj.name, plugin_obj_from_zip.name)
        self.assertEqual(plugin_obj.version, plugin_obj_from_zip.version)
        self.assertEqual(plugin_obj.folder_name, plugin_obj_from_zip.folder_name)
        self.assertEqual(plugin_obj.url, sample_plugin_complex.get("url"))
        self.assertEqual(plugin_obj.download_url, sample_plugin_complex.get("url"))
        self.assertEqual(plugin_obj.uri_to_zip, sample_plugin_complex.get("url"))

        # clean up
        rmtree(path=local_plugin_download.parent, ignore_errors=True)

    def test_qplugin_versions_comparison_semver(self):
        """Test plugin compare versions semver"""
        plugin_v1: QgisPlugin = QgisPlugin.from_dict(
            {
                "name": "Sample plugin",
                "version": "1.0.0",
            }
        )

        plugin_v2: QgisPlugin = QgisPlugin.from_dict(
            {
                "name": "Sample plugin",
                "version": "1.1.0",
            }
        )

        plugin_v3: QgisPlugin = QgisPlugin.from_dict(
            {
                "name": "Sample plugin",
                "version": "3.1.0",
            }
        )

        self.assertTrue(plugin_v1.is_older_than(plugin_v2.version))
        self.assertTrue(plugin_v1.is_older_than(plugin_v2))
        self.assertTrue(plugin_v1.is_older_than(plugin_v3.version))
        self.assertTrue(plugin_v1.is_older_than(plugin_v3))
        self.assertTrue(plugin_v2.is_older_than(plugin_v3.version))
        self.assertTrue(plugin_v2.is_older_than(plugin_v3))
        self.assertFalse(plugin_v2.is_older_than(plugin_v1))

    def test_qplugin_versions_comparison_semver_prefixed(self):
        """Test plugin compare versions semver with a prefix"""
        plugin_v1: QgisPlugin = QgisPlugin.from_dict(
            {
                "name": "Sample plugin",
                "version": "v1.0.0",
            }
        )

        plugin_v2: QgisPlugin = QgisPlugin.from_dict(
            {
                "name": "Sample plugin",
                "version": "v1.1.0",
            }
        )

        plugin_v3: QgisPlugin = QgisPlugin.from_dict(
            {
                "name": "Sample plugin",
                "version": "v3.1.0",
            }
        )

        self.assertTrue(plugin_v1.is_older_than(plugin_v2.version))
        self.assertTrue(plugin_v1.is_older_than(plugin_v2))
        self.assertTrue(plugin_v1.is_older_than(plugin_v3.version))
        self.assertTrue(plugin_v1.is_older_than(plugin_v3))
        self.assertTrue(plugin_v2.is_older_than(plugin_v3.version))
        self.assertTrue(plugin_v2.is_older_than(plugin_v3))
        self.assertFalse(plugin_v2.is_older_than(plugin_v1))

    def test_qplugin_versions_comparison_calver(self):
        """Test plugin compare versions calver"""
        plugin_v1: QgisPlugin = QgisPlugin.from_dict(
            {"name": "Sample plugin", "version": "2021.9.10"}
        )

        plugin_v2: QgisPlugin = QgisPlugin.from_dict(
            {
                "name": "Sample plugin",
                "version": "2021.12.10",
            }
        )

        plugin_v3: QgisPlugin = QgisPlugin.from_dict(
            {
                "name": "Sample plugin",
                "version": "2023.2.10",
            }
        )

        self.assertTrue(plugin_v1.is_older_than(plugin_v2.version))
        self.assertTrue(plugin_v1.is_older_than(plugin_v2))
        self.assertTrue(plugin_v1.is_older_than(plugin_v3.version))
        self.assertTrue(plugin_v1.is_older_than(plugin_v3))
        self.assertTrue(plugin_v2.is_older_than(plugin_v3.version))
        self.assertTrue(plugin_v2.is_older_than(plugin_v3))
        self.assertFalse(plugin_v2.is_older_than(plugin_v1))

    def test_qplugin_versions_comparison_bad(self):
        """Test plugin compare versions issues"""
        plugin_v1: QgisPlugin = QgisPlugin.from_dict(
            {"name": "Sample plugin", "version": "2021.9.10"}
        )

        plugin_v2: QgisPlugin = QgisPlugin.from_dict(
            {
                "name": "Sample plugin 2",
                "version": "2021.12.10",
            }
        )

        self.assertTrue(plugin_v1.is_older_than(plugin_v2.version))
        self.assertFalse(plugin_v2.is_older_than(plugin_v1))

        plugin_bad_version: QgisPlugin = QgisPlugin.from_dict(
            {
                "name": "Sample plugin",
                "version": "march 2022",
            }
        )

        self.assertIsNone(plugin_v1.is_older_than(plugin_bad_version))


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
