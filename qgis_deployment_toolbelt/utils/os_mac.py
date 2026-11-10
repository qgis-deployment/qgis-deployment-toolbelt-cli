#! python3  # noqa: E265

"""Utilities specific for macOS.

For now, Desktop and applications folders follow the same conventions as on Linux.
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# standard
from pathlib import Path

# project
from qgis_deployment_toolbelt.utils.os_linux import (
    get_user_desktop_folder,
    get_user_startmenu_folder,
)


__all__ = [
    "get_user_desktop_folder",
    "get_user_home_folder",
    "get_user_startmenu_folder",
]


# #############################################################################
# ########## Functions #############
# ##################################


def get_user_home_folder() -> Path:
    """Return the user home folder.

    Returns:
        Path: path to the user home
    """
    return Path("~").expanduser()
