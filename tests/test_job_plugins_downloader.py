#! python3  # noqa E265

"""Usage from the repo root folder:

.. code-block:: python

    # for whole test
    python -m unittest tests.test_job_plugins_downloader
    # for specific
    python -m unittest tests.test_job_plugins_downloader.TestJobPluginsDownloader.test_filter_plugins_location_from_profile_json
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import json
import tempfile
import unittest
from pathlib import Path

# package
from qgis_deployment_toolbelt.jobs.job_plugins_downloader import JobPluginsDownloader
from qgis_deployment_toolbelt.profiles.qdt_profile import QdtProfile


# #############################################################################
# ########## Classes ###############
# ##################################


class TestJobPluginsDownloader(unittest.TestCase):
    """Test plugins downloader job."""

    # -- Tests -------------------------------------------------------------------
    def test_filter_plugins_location_from_profile_json(self):
        """Plugins loaded from a profile.json must be downloaded or copied according
        to their location, whatever the way it's set (or not set) in the file."""
        # label: (plugin as written in profile.json, expected job action)
        cases: dict[str, tuple[dict, str]] = {
            "explicit url, no location": (
                {
                    "name": "Custom repo plugin",
                    "version": "1.1.1",
                    "url": "https://plugins.example.org/download.php?plugin=custom",
                },
                "download",
            ),
            "official, no url, no location": (
                {
                    "name": "Official plugin",
                    "folder_name": "official_plugin",
                    "version": "1.0.0",
                    "official_repository": True,
                },
                "download",
            ),
            "location remote": (
                {
                    "name": "Remote plugin",
                    "version": "1.0.0",
                    "url": "https://plugins.example.org/remote.zip",
                    "location": "remote",
                },
                "download",
            ),
            "location local": (
                {
                    "name": "Local plugin",
                    "version": "1.0.0",
                    "url": "C:/plugins/local.zip",
                    "location": "local",
                },
                "copy",
            ),
            "legacy 'type' key": (
                {
                    "name": "Legacy plugin",
                    "version": "1.0.0",
                    "url": "https://plugins.example.org/legacy.zip",
                    "type": "remote",
                },
                "download",
            ),
            "location with another case": (
                {
                    "name": "Local plugin case",
                    "version": "1.0.0",
                    "url": "C:/plugins/local_case.zip",
                    "location": "Local",
                },
                "copy",
            ),
            "invalid location": (
                {
                    "name": "Invalid location plugin",
                    "version": "1.0.0",
                    "url": "https://plugins.example.org/invalid.zip",
                    "location": "distant",
                },
                "download",
            ),
        }

        with tempfile.TemporaryDirectory(
            prefix="QDT_test_plugins_downloader_location_"
        ) as tmp_dir:
            profile_json = Path(tmp_dir, "profile.json")
            profile_json.write_text(
                json.dumps(
                    {
                        "name": "test_plugins_location",
                        "folder_name": "test_plugins_location",
                        "version": "1.0.0",
                        "plugins": [plugin for plugin, _ in cases.values()],
                    }
                ),
                encoding="UTF-8",
            )
            profile = QdtProfile.from_json(
                profile_json_path=profile_json, profile_folder=Path(tmp_dir)
            )

            job = JobPluginsDownloader(options={})
            job.qdt_plugins_folder = Path(tmp_dir)

            to_download = {
                p.name for p in job.filter_list_downloadable_plugins(profile.plugins)
            }
            to_copy = {
                p.name for p in job.filter_list_copiable_plugins(profile.plugins)
            }

            for label, (plugin, expected_action) in cases.items():
                with self.subTest(label):
                    self.assertEqual(
                        plugin["name"] in to_download, expected_action == "download"
                    )
                    self.assertEqual(
                        plugin["name"] in to_copy, expected_action == "copy"
                    )


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
