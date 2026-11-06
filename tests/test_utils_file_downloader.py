#! python3  # noqa E265

"""
Usage from the repo root folder:

.. code-block:: bash
    # for whole tests
    python -m unittest tests.test_utils_file_downloader
    # for specific test
    python -m unittest tests.test_utils_file_downloader.TestUtilsFileDownloader.test_download_file_exists
"""

# standard library
import filecmp
import tempfile
import unittest
from os import environ, getenv
from pathlib import Path
from unittest.mock import patch

# 3rd party
from requests import exceptions as requests_exceptions

# project
from qgis_deployment_toolbelt.utils.file_downloader import (
    TruststoreAdapter,
    download_remote_file_to_local,
    get_http_session,
)


# ############################################################################
# ########## Classes #############
# ################################


class TestUtilsFileDownloader(unittest.TestCase):
    """Test package utilities."""

    def authorization_header(self) -> str | None:
        """Define authorization header if GITHUB_TOKEN available

        Returns:
            str | None: authorization header, None if GITHUB_TOKEN unavailable
        """
        if getenv("GITHUB_TOKEN"):
            return f"Bearer {getenv('GITHUB_TOKEN')}"
        return None

    def test_get_http_session_default(self):
        """Test HTTP session built without QDT network settings."""
        with patch.dict(environ):
            environ.pop("QDT_SSL_VERIFY", None)
            environ.pop("QDT_SSL_USE_SYSTEM_STORES", None)
            http_session = get_http_session(user_agent="qdt-test/0.0.0")

        with http_session:
            self.assertEqual(http_session.headers["User-Agent"], "qdt-test/0.0.0")
            self.assertTrue(http_session.verify)
            self.assertNotIsInstance(
                http_session.get_adapter("https://example.org"), TruststoreAdapter
            )

    def test_get_http_session_ssl_settings(self):
        """Test HTTP session honors QDT_SSL_VERIFY and QDT_SSL_USE_SYSTEM_STORES."""
        with (
            patch.dict(
                environ,
                {"QDT_SSL_VERIFY": "false", "QDT_SSL_USE_SYSTEM_STORES": "true"},
            ),
            get_http_session() as http_session,
        ):
            self.assertFalse(http_session.verify)
            self.assertIsInstance(
                http_session.get_adapter("https://example.org"), TruststoreAdapter
            )
            # plain HTTP is not affected
            self.assertNotIsInstance(
                http_session.get_adapter("http://example.org"), TruststoreAdapter
            )

    def test_download_file_exists(self):
        """Test download remote file locally to a file which already exists."""
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_downloader_", ignore_cleanup_errors=True
        ) as tmpdirname:
            # file that already exist locally
            downloaded_file = download_remote_file_to_local(
                remote_url_to_download="https://raw.githubusercontent.com/qgis-deployment/qgis-deployment-toolbelt-cli/main/README.md",
                local_file_path=Path(tmpdirname).joinpath("README_from_remote.md"),
                authorization=self.authorization_header(),
            )
            self.assertIsInstance(downloaded_file, Path)
            self.assertTrue(downloaded_file.exists())
            self.assertTrue(downloaded_file.is_file())

        # disabling stream mode
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_downloader_nostream_", ignore_cleanup_errors=True
        ) as tmpdirname:
            # file that already exist locally
            downloaded_file = download_remote_file_to_local(
                remote_url_to_download="https://raw.githubusercontent.com/qgis-deployment/qgis-deployment-toolbelt-cli/main/README.md",
                local_file_path=Path(tmpdirname).joinpath("README_from_remote.md"),
                use_stream=False,
                authorization=self.authorization_header(),
            )
            self.assertIsInstance(downloaded_file, Path)
            self.assertTrue(downloaded_file.exists())
            self.assertTrue(downloaded_file.is_file())

    def test_download_url_with_params(self):
        """Test download remote file locally from url with params"""
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_downloader_", ignore_cleanup_errors=True
        ) as tmpdirname:
            # file that already exist locally
            downloaded_file_one = download_remote_file_to_local(
                remote_url_to_download="https://raw.githubusercontent.com/qgis-deployment/qgis-deployment-toolbelt-cli/main/README.md",
                local_file_path=Path(tmpdirname).joinpath("README1.md"),
                authorization=self.authorization_header(),
            )
            self.assertIsInstance(downloaded_file_one, Path)
            self.assertTrue(downloaded_file_one.exists())
            self.assertTrue(downloaded_file_one.is_file())

            downloaded_file_two = download_remote_file_to_local(
                remote_url_to_download="https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/blob/main/README.md?raw=true",
                local_file_path=Path(tmpdirname).joinpath("README2.md"),
                authorization=self.authorization_header(),
            )
            self.assertIsInstance(downloaded_file_two, Path)
            self.assertTrue(downloaded_file_two.exists())
            self.assertTrue(downloaded_file_two.is_file())

            self.assertTrue(filecmp.cmp(downloaded_file_one, downloaded_file_two))

    def test_download_file_raise_http_error(self):
        """Test download handling an HTTP error."""
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_downloader_", ignore_cleanup_errors=True
        ) as tmpdirname:
            target_path = Path(tmpdirname).joinpath("dl_404.html")
            with self.assertRaises(requests_exceptions.HTTPError):
                download_remote_file_to_local(
                    remote_url_to_download="https://qgis.org/fake-page",
                    local_file_path=target_path,
                )
            self.assertFalse(target_path.exists())
            self.assertFalse(target_path.is_file())

    def test_download_file_raise_url_error(self):
        """Test download with a bad URL."""
        with tempfile.TemporaryDirectory(
            prefix="qdt_test_downloader_", ignore_cleanup_errors=True
        ) as tmpdirname:
            target_path = Path(tmpdirname).joinpath("fake_file.dmg")
            with self.assertRaises(requests_exceptions.ConnectionError):
                download_remote_file_to_local(
                    remote_url_to_download="https://fake_url/youpi.dmg",
                    local_file_path=target_path,
                )
            self.assertFalse(target_path.exists())
            self.assertFalse(target_path.is_file())


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
