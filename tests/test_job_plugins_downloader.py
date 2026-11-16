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
from unittest.mock import patch

# package
from qgis_deployment_toolbelt.jobs.job_plugins_downloader import JobPluginsDownloader
from qgis_deployment_toolbelt.plugins.plugin import QgisPlugin
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

    def test_download_remote_plugins_failures_are_counted(self):
        """Test a failed download is reported as failed, whatever the number of
        threads (in multithreaded mode, failures used to be counted as success)."""
        plugins = [
            QgisPlugin(name="good_plugin", url="https://example.org/good.zip"),
            QgisPlugin(name="broken_plugin", url="https://example.org/broken.zip"),
            QgisPlugin(name="other_good", url="https://example.org/other.zip"),
        ]

        def fake_download(
            remote_url_to_download: str, local_file_path: Path, **_: object
        ) -> Path:
            if "broken" in remote_url_to_download:
                raise ConnectionError(f"404 Not Found for {remote_url_to_download}")
            local_file_path.write_bytes(b"fake zip")
            return local_file_path

        job = JobPluginsDownloader(options={})
        for threads in (1, 5):
            with (
                self.subTest(threads=threads),
                tempfile.TemporaryDirectory(
                    prefix="QDT_test_plugins_downloader_failures_"
                ) as tmp_dir,
                patch(
                    "qgis_deployment_toolbelt.jobs.job_plugins_downloader."
                    "download_remote_file_to_local",
                    side_effect=fake_download,
                ),
                self.assertLogs(
                    "qgis_deployment_toolbelt.jobs.job_plugins_downloader",
                    level="ERROR",
                ) as logs,
            ):
                downloaded, failed = job.download_remote_plugins(
                    plugins_to_download=plugins,
                    destination_parent_folder=Path(tmp_dir),
                    threads=threads,
                )

            self.assertEqual(
                [p.name for p in downloaded], ["good_plugin", "other_good"]
            )
            self.assertEqual([p.name for p in failed], ["broken_plugin"])
            self.assertTrue(any("broken_plugin" in line for line in logs.output))


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
