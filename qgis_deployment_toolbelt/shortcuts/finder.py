#! python3  # noqa: E265

"""Shortcuts finder."""


# #############################################################################
# ########## Libraries #############
# ##################################

# standard
import logging
from pathlib import Path
from sys import platform as opersys

# package
from qgis_deployment_toolbelt.constants import (
    QDT_SHORTCUT_DESCRIPTION_PREFIX,
)
from qgis_deployment_toolbelt.utils.os_router import (
    get_user_desktop_folder,
    get_user_startmenu_folder,
    read_shortcut,
)


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Functions #############
# ##################################


def list_qdt_shortcuts(shortcut_extension: str) -> dict[Path, Path]:
    """List shortcuts marked as created by QDT (description starting with the QDT
    mark) in the user desktop and start menu folders, with the profile folder
    they target.

    Args:
        shortcut_extension (str): extension of shortcut files

    Returns:
        dict[Path, Path]: targeted profile folder by shortcut path
    """
    if read_shortcut is None:
        logger.debug(f"Listing shortcuts is not supported on {opersys}.")
        return {}

    qdt_shortcuts: dict[Path, Path] = {}
    for folder in (get_user_desktop_folder(), get_user_startmenu_folder()):
        if not folder.is_dir():
            continue
        for shortcut_path in sorted(folder.glob(f"*{shortcut_extension}")):
            shortcut = read_shortcut(shortcut_path)
            if shortcut is None:
                continue
            description, profile_folder = shortcut
            if (
                description.startswith(QDT_SHORTCUT_DESCRIPTION_PREFIX)
                and isinstance(profile_folder, Path)
                and profile_folder.is_absolute()
            ):
                qdt_shortcuts[shortcut_path] = profile_folder

    return qdt_shortcuts
