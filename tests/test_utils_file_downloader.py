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
import tempfile
import unittest
from os import environ
from pathlib import Path
from unittest.mock import patch

# 3rd party
import pytest
from pytest_httpserver import HTTPServer
from requests import exceptions as requests_exceptions

# project
from qgis_deployment_toolbelt.utils.file_downloader import (
    TruststoreAdapter,
    download_remote_file_to_local,
    get_http_session,
)


# ############################################################################
# ########## Globals #############
# ################################

# bigger than the default chunk size, to download it in several chunks
SAMPLE_FILE_CONTENT: bytes = b"# QDT test file\n" + b"x" * 20_000


# ############################################################################
# ########## Classes #############
# ################################


class TestUtilsFileDownloader(unittest.TestCase):
    """Test package utilities."""

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
# ########## Functions ###########
# ################################


@pytest.mark.parametrize("use_stream", [True, False], ids=["stream", "no_stream"])
def test_download_file(httpserver: HTTPServer, tmp_path: Path, use_stream: bool):
    """Test download remote file locally, with and without stream mode."""
    httpserver.expect_oneshot_request("/README.md").respond_with_data(
        SAMPLE_FILE_CONTENT, content_type="text/markdown"
    )

    downloaded_file = download_remote_file_to_local(
        remote_url_to_download=httpserver.url_for("/README.md"),
        local_file_path=tmp_path / "README.md",
        use_stream=use_stream,
    )

    assert downloaded_file == tmp_path / "README.md"
    assert downloaded_file.read_bytes() == SAMPLE_FILE_CONTENT
    assert not httpserver.oneshot_handlers


def test_download_file_exists(httpserver: HTTPServer, tmp_path: Path):
    """Test download remote file locally to a file which already exists."""
    httpserver.expect_oneshot_request("/README.md").respond_with_data(
        SAMPLE_FILE_CONTENT, content_type="text/markdown"
    )
    local_file = tmp_path / "README.md"
    local_file.write_text("previous version", encoding="UTF-8")

    downloaded_file = download_remote_file_to_local(
        remote_url_to_download=httpserver.url_for("/README.md"),
        local_file_path=local_file,
    )

    assert downloaded_file.read_bytes() == SAMPLE_FILE_CONTENT
    assert not httpserver.oneshot_handlers


def test_download_url_with_params(httpserver: HTTPServer, tmp_path: Path):
    """Test download remote file locally from url with params: they must be sent."""
    httpserver.expect_oneshot_request(
        "/README.md", query_string={"raw": "true", "ref": "main"}
    ).respond_with_data(SAMPLE_FILE_CONTENT, content_type="text/markdown")

    downloaded_file = download_remote_file_to_local(
        remote_url_to_download=httpserver.url_for("/README.md?raw=true&ref=main"),
        local_file_path=tmp_path / "README.md",
    )

    assert downloaded_file.read_bytes() == SAMPLE_FILE_CONTENT
    # the request matched the expected query string
    assert not httpserver.oneshot_handlers


def test_download_file_headers(httpserver: HTTPServer, tmp_path: Path):
    """Test that user agent, content type and authorization are sent as headers."""
    httpserver.expect_oneshot_request(
        "/plugin.zip",
        headers={
            "Accept": "application/zip",
            "Authorization": "Bearer fake-token",
            "User-Agent": "qdt-test/0.0.0",
        },
    ).respond_with_data(b"PK", content_type="application/zip")

    download_remote_file_to_local(
        remote_url_to_download=httpserver.url_for("/plugin.zip"),
        local_file_path=tmp_path / "plugin.zip",
        user_agent="qdt-test/0.0.0",
        content_type="application/zip",
        authorization="Bearer fake-token",
    )

    assert not httpserver.oneshot_handlers


@pytest.mark.parametrize("status", [404, 503])
def test_download_file_raise_http_error(
    httpserver: HTTPServer, tmp_path: Path, status: int
):
    """Test download handling an HTTP error: nothing is written locally."""
    httpserver.expect_oneshot_request("/fake-page").respond_with_data(
        "error", status=status
    )
    target_path = tmp_path / "dl_error.html"

    with pytest.raises(requests_exceptions.HTTPError):
        download_remote_file_to_local(
            remote_url_to_download=httpserver.url_for("/fake-page"),
            local_file_path=target_path,
        )

    assert not target_path.exists()


# ############################################################################
# ####### Stand-alone run ########
# ################################
if __name__ == "__main__":
    unittest.main()
