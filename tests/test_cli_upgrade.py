#! python3  # noqa: E265

"""
Test CLI's clean command.

Author: Julien Moura (Oslandia)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
import unittest

# 3rd party library
import pytest
from validators import url

# module to test
from qgis_deployment_toolbelt import cli
from qgis_deployment_toolbelt.__about__ import __uri_repository__
from qgis_deployment_toolbelt.commands.upgrade import (
    get_download_url_for_os,
    get_latest_release,
    replace_domain,
)
from qgis_deployment_toolbelt.constants import SUPPORTED_OPERATING_SYSTEMS_CODENAMES


# #############################################################################
# ######## Functions ###############
# ##################################


def test_cli_upgrade_check_only(capsys):
    """Test CLI upgrade check only."""
    with pytest.raises(SystemExit):
        cli.main(["upgrade", "-c"])

    _, err = capsys.readouterr()

    assert err == ""


def test_cli_upgrade_download(capsys):
    """Test CLI upgrade ."""
    with pytest.raises(SystemExit):
        cli.main(["upgrade", "-n", "-w", "tests/"])

    _, err = capsys.readouterr()

    assert err == ""


# ############################################################################
# ########## Classes #############
# ################################


class TestUpgradeUtils(unittest.TestCase):
    """Test upgrade utilities."""

    def test_release_assets_download_links(self):
        """Test utils to retrieve latest version download links."""
        api_url_from_repo_url = replace_domain(
            url=__uri_repository__, new_domain="api.github.com/repos"
        )
        self.assertTrue(url(api_url_from_repo_url))
        self.assertIsInstance(api_url_from_repo_url, str)

        latest_release = get_latest_release(api_url_from_repo_url)
        self.assertIsInstance(latest_release, dict)
        self.assertTrue("assets" in latest_release)

        dl_hyperlinks = [
            get_download_url_for_os(latest_release.get("assets"), override_opersys=os)[
                0
            ]
            for os in SUPPORTED_OPERATING_SYSTEMS_CODENAMES
        ]
        self.assertTrue(len(dl_hyperlinks), 3)

        self.assertTrue(
            all(
                [
                    dl_url.startswith("https")
                    for dl_url in dl_hyperlinks
                    if isinstance(dl_url, str)
                ]
            )
        )


# #############################################################################
# ######## Standalone ##############
# ##################################
if __name__ == "__main__":
    unittest.main()
