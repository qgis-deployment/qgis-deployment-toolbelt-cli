# #############################################################################
# ########## Libraries #############
# ##################################

# standard
import logging
from configparser import ConfigParser, Error as ConfigParserError
from pathlib import Path
from sys import platform as opersys


# Imports depending on operating system
if opersys == "win32":
    """windows"""
    import pythoncom
    import win32com.client

# package
from qgis_deployment_toolbelt.constants import (
    QDT_SHORTCUT_FREEDESKTOP_PATTERN,
    QDT_SHORTCUT_WINDOWS_PREFIX,
)
from qgis_deployment_toolbelt.shortcuts.shortcuts_handler import (
    logger,
)
from qgis_deployment_toolbelt.utils.os_router import (
    get_user_desktop_folder,
    get_user_startmenu_folder,
)


# -- Globals --

# logs
logger = logging.getLogger(__name__)


# -- Functions --


def _read_win32_shortcut_profile_folder(shortcut_path: Path) -> Path | None:
    """Read the profile folder targeted by a Windows shortcut created by QDT, i.e.
    its working directory, if its description is the one set by QDT.

    Args:
        shortcut_path (Path): path to the .lnk file

    Returns:
        Path | None: targeted profile folder or None if the shortcut has not been
            created by QDT or can't be read
    """
    win_shell = win32com.client.Dispatch("Wscript.Shell")
    try:
        # CreateShortCut opens the shortcut if it already exists
        wscript = win_shell.CreateShortCut(str(shortcut_path))
        description, work_dir = wscript.Description, wscript.WorkingDirectory
    except pythoncom.com_error as err:
        logger.debug(f"Unable to read shortcut {shortcut_path}: {err}")
        return None

    if not description.startswith(QDT_SHORTCUT_WINDOWS_PREFIX) or not work_dir:
        return None
    return Path(work_dir)


# #############################################################################
# ########## Functions #############
# ##################################


def _read_freedesktop_shortcut_profile_folder(shortcut_path: Path) -> Path | None:
    """Read the profile folder targeted by a FreeDesktop shortcut created by QDT,
    from its 'ProfileFolder' desktop action.

    Args:
        shortcut_path (Path): path to the .desktop file

    Returns:
        Path | None: targeted profile folder or None if it can't be read
    """
    parser = ConfigParser(interpolation=None)
    try:
        parser.read(shortcut_path, encoding="UTF-8")
        exec_value = parser.get("Desktop Action ProfileFolder", "Exec")
    except (ConfigParserError, UnicodeDecodeError) as err:
        logger.debug(f"Unable to read profile folder from {shortcut_path}: {err}")
        return None

    profile_folder = exec_value.removeprefix("xdg-open").strip()
    return Path(profile_folder) if profile_folder else None


def list_qdt_shortcuts() -> dict[Path, Path]:
    """List shortcuts created by QDT in the user desktop and start menu folders,
    with the profile folder they target.

    Returns:
        dict[Path, Path]: targetted profile folder by shortcut path
    """
    if opersys == "win32":
        pattern, shortcut_reader = "*.lnk", _read_win32_shortcut_profile_folder
    else:
        pattern = QDT_SHORTCUT_FREEDESKTOP_PATTERN
        shortcut_reader = _read_freedesktop_shortcut_profile_folder

    qdt_shortcuts: dict[Path, Path] = {}
    for folder in (get_user_desktop_folder(), get_user_startmenu_folder()):
        if not isinstance(folder, Path) or not folder.is_dir():
            continue
        for shortcut_path in sorted(folder.glob(pattern)):
            profile_folder = shortcut_reader(shortcut_path)
            if isinstance(profile_folder, Path) and profile_folder.is_absolute():
                qdt_shortcuts[shortcut_path] = profile_folder

    return qdt_shortcuts
