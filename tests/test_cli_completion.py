#! python3  # noqa: E265

"""
Test CLI's completion subcommand.

Author: Julien M. (https://github.com/guts)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard library
from unittest.mock import patch

# 3rd party
import pytest

# project
from qgis_deployment_toolbelt import cli
from qgis_deployment_toolbelt.commands import cmd_completion


# #############################################################################
# ######## Fixtures ################
# ##################################


@pytest.fixture(scope="session")
def argcomplete_available():
    """Skip any test using this fixture when argcomplete is not installed."""
    pytest.importorskip(
        "argcomplete",
        reason="argcomplete is not installed. Install it with: "
        "pip install 'qgis-deployment-toolbelt[completion]'",
    )


# #############################################################################
# ######## Tests ###################
# ##################################


def test_cli_completion_without_argcomplete(capsys):
    """When argcomplete is not available, the command exits with code 1.

    This test always runs, regardless of whether argcomplete is installed.
    """
    with patch.object(cmd_completion, "HAS_ARGCOMPLETE", False):
        with pytest.raises(SystemExit) as exc_info:
            cli.main(["completion"])

    assert exc_info.value.code == 1


@pytest.mark.parametrize("option", ("-h", "--help"))
def test_cli_completion_help(capsys, option):
    """Test completion subcommand help."""
    with pytest.raises(SystemExit):
        cli.main(["completion", option])

    _, err = capsys.readouterr()
    assert err == ""
