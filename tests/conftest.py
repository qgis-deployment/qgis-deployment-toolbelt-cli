#! python3  # noqa: E265

"""Shared pytest configuration.

Isolates the test session from the user's real environment:

- on Linux and macOS, ``HOME`` and the XDG base directories point to a temporary
  folder, so that tests never write into the real shell profile (``~/.profile``),
  caches, QGIS profiles, desktop or applications menu;
- every test starts with the environment variables it was given and leaves them as
  they were, so that a test can no longer leak variables into the next ones.

The redirection happens when this module is loaded, i.e. before pytest imports the
test modules, because several paths are computed at import time from
``Path.home()`` (see ``constants.py`` and ``utils/os_linux.py``).

On Windows, the user folders come from ``USERPROFILE``, ``APPDATA`` and the
registry: they are left untouched.

Provides the ``qgis_plugins_repository`` fixture, a local HTTP server standing for the
official QGIS plugins repository (plugins.qgis.org), so that tests don't depend on its
availability.
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import os
import re
import shutil
import sys
import tempfile
from collections.abc import Iterator
from pathlib import Path

# 3rd party
import pytest
from pytest_httpserver import HTTPServer
from werkzeug import Request, Response

# test helpers
from tests.helpers import build_fake_plugin_zip


# #############################################################################
# ########## Session-wide isolation ################
# ##################################################

_ISOLATED_HOME: Path | None = None

if sys.platform != "win32":
    _ISOLATED_HOME = Path(tempfile.mkdtemp(prefix="qdt-tests-home-"))
    os.environ["HOME"] = str(_ISOLATED_HOME)
    for xdg_var, sub_path in (
        ("XDG_CACHE_HOME", ".cache"),
        ("XDG_CONFIG_HOME", ".config"),
        ("XDG_DATA_HOME", ".local/share"),
        ("XDG_STATE_HOME", ".local/state"),
    ):
        xdg_folder = _ISOLATED_HOME / sub_path
        xdg_folder.mkdir(parents=True, exist_ok=True)
        os.environ[xdg_var] = str(xdg_folder)


def pytest_report_header(config: pytest.Config) -> str:
    """Display where the user folder of the test session is.

    Args:
        config: pytest configuration

    Returns:
        line added to the header of the test report
    """
    if _ISOLATED_HOME is None:
        return "QDT tests: user folder not isolated on this platform"
    return f"QDT tests: isolated HOME in {_ISOLATED_HOME}"


def pytest_unconfigure(config: pytest.Config) -> None:
    """Remove the isolated user folder at the end of the session.

    Args:
        config: pytest configuration
    """
    if _ISOLATED_HOME is not None:
        shutil.rmtree(_ISOLATED_HOME, ignore_errors=True)


# #############################################################################
# ########## Fixtures ##############
# ##################################


@pytest.fixture(autouse=True)
def restore_environment_variables():
    """Restore the environment variables as they were before each test."""
    environment_before = dict(os.environ)
    yield
    for name in set(os.environ) - set(environment_before):
        del os.environ[name]
    for name, value in environment_before.items():
        if os.environ.get(name) != value:
            os.environ[name] = value


# #############################################################################
# ########## Fake QGIS plugins repository ################
# ########################################################

# download URL path of a plugin in the official repository, relative to its base URL
RE_FAKE_PLUGIN_DOWNLOAD_PATH = re.compile(
    r"^/plugins/(?P<folder_name>[^/]+)/version/(?P<version>[^/]+)/download/$"
)


def _serve_fake_plugin(request: Request) -> Response:
    """Answer a plugin download request with a ZIP archive matching the requested
    plugin folder name and version.

    Args:
        request: incoming HTTP request

    Returns:
        HTTP response with the plugin ZIP archive
    """
    match = RE_FAKE_PLUGIN_DOWNLOAD_PATH.match(request.path)
    return Response(
        build_fake_plugin_zip(
            folder_name=match.group("folder_name"), version=match.group("version")
        ),
        content_type="application/zip",
    )


@pytest.fixture
def qgis_plugins_repository(monkeypatch: pytest.MonkeyPatch) -> Iterator[HTTPServer]:
    """Simulate the official QGIS plugins repository with a local HTTP server.

    Any ``/plugins/<folder_name>/version/<version>/download/`` request returns a
    minimal plugin ZIP archive built on the fly. The official repository URLs used by
    the plugin model are redirected to this server for the duration of the test.

    Args:
        monkeypatch: pytest fixture used to redirect the official repository URLs

    Yields:
        started HTTP server
    """
    server = HTTPServer()  # random free port
    server.expect_request(RE_FAKE_PLUGIN_DOWNLOAD_PATH).respond_with_handler(
        _serve_fake_plugin
    )
    server.start()

    base_url = server.url_for("/")
    monkeypatch.setattr(
        "qgis_deployment_toolbelt.plugins.plugin.QGIS_PLUGINS_OFFICIAL_REPOSITORY_URL_BASE",
        base_url,
    )
    monkeypatch.setattr(
        "qgis_deployment_toolbelt.plugins.plugin.QGIS_PLUGINS_OFFICIAL_REPOSITORY_XML",
        f"{base_url}plugins/plugins.xml",
    )

    yield server

    server.clear()
    if server.is_running():
        server.stop()
