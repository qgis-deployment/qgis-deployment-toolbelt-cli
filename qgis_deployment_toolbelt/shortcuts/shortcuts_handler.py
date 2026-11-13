#! python3  # noqa: E265

"""
Cross-platform shortcuts manager. Derived from pycrosskit, by  Jiri Otoupal.
See also: https://github.com/newville/pyshortcuts/
Author: Julien Moura (https://github.com/guts)
"""

# #############################################################################
# ########## Libraries #############
# ##################################
# standard
import logging
import shlex
import stat
import sys
from collections.abc import Iterable
from pathlib import Path
from string import Template
from sys import platform as opersys


# Imports depending on operating system
if opersys == "win32":
    """windows"""
    import pythoncom
    import win32com.client

# package
from qgis_deployment_toolbelt.__about__ import __version__
from qgis_deployment_toolbelt.constants import (
    QDT_SHORTCUT_DESCRIPTION_PREFIX,
    QGIS_BIN_WINDOWS_FILENAME,
    QGIS_LTR_BIN_WINDOWS_FILENAME,
    OSConfiguration,
)
from qgis_deployment_toolbelt.utils.check_path import check_path
from qgis_deployment_toolbelt.utils.frozen_app import is_running_pyinstaller
from qgis_deployment_toolbelt.utils.os_linux import escape_freedesktop_exec_quoted
from qgis_deployment_toolbelt.utils.os_router import (
    get_user_desktop_folder,
    get_user_home_folder,
    get_user_startmenu_folder,
)
from qgis_deployment_toolbelt.utils.slugger import sluggy


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Classes ###############
# ##################################


class ApplicationShortcut:
    def __init__(
        self,
        name: str,
        exec_path: str | Path,
        exec_arguments: Iterable[str] | None = None,
        description: str | None = None,
        icon_path: str | Path | None = None,
        work_dir: str | Path | None = None,
    ):
        """Initialize a shortcut object.

        Args:
            name (str): name of the shortcut that will be created
            exec_path (str | Path): path to the executable (which should exist)
            exec_arguments (Iterable[str] | None, optional): list of arguments and \
                options to pass to the executable. Defaults to None.
            description (str | None, optional): shortcut description. Defaults to None.
            icon_path (str | Path | None, optional): path to icon file. Defaults to None.
            work_dir (str | Path | None, optional): current folder where to start the \
                executable. Defaults to None. In QDT, it's the profile folder.

        Raises:
            ValueError: if shortcut name contains invalid characters (depending on \
                operating system)
        """
        # retrieve operating system specific configuration
        self.os_config = OSConfiguration.from_opersys()

        # -- CHECK TYPE AND STORE ATTRIBUTES
        # mandatory
        if isinstance(name, str):
            if not self.os_config.valid_shortcut_name(name):
                raise ValueError(f"Shortcut name {name} contains invalid characters.")
            self.name = name
        else:
            raise TypeError(f"Shortcut name must be a string, not {type(name)}.")

        if isinstance(exec_path, (str, Path)):
            self.exec_path = Path(exec_path)
            if not self.exec_path.exists():
                # helper to handle common typo error on executable name on Windows
                if (
                    self.exec_path.name.endswith(QGIS_BIN_WINDOWS_FILENAME)
                    and self.exec_path.with_name(QGIS_LTR_BIN_WINDOWS_FILENAME).exists()
                ):
                    logger.warning(
                        f"Executable set does not exist: {self.exec_path} "
                        f"but {self.exec_path.with_name('qgis-ltr-bin.exe')} does, so "
                        "this one will be used instead. Check and fix your scenario."
                    )
                    self.exec_path = self.exec_path.with_name(
                        QGIS_LTR_BIN_WINDOWS_FILENAME
                    )
                elif (
                    self.exec_path.name.endswith(QGIS_LTR_BIN_WINDOWS_FILENAME)
                    and self.exec_path.with_name(QGIS_BIN_WINDOWS_FILENAME).exists()
                ):
                    logger.warning(
                        f"Executable set does not exist: {self.exec_path} "
                        f"but {self.exec_path.with_name('qgis-bin.exe')} does, so "
                        "this one will be used instead. Check and fix your scenario."
                    )
                    self.exec_path = self.exec_path.with_name(QGIS_BIN_WINDOWS_FILENAME)
                else:
                    logger.warning(
                        f"Executable does not exist: {self.exec_path}. "
                        "Shortcuts might not work. Check and fix your scenario."
                    )
        else:
            raise TypeError(
                f"exec_path must be a string or pathlib.Path, not {type(exec_path)}"
            )

        # optional
        if isinstance(exec_arguments, (tuple, list, type(None))):
            self.exec_arguments = self.check_exec_arguments(exec_arguments)
        else:
            raise TypeError(
                f"If defined, exec_arguments must be a tuple or list, not {type(exec_arguments)}"
            )
        if isinstance(description, (str, type(None))):
            self.description = description
        else:
            raise TypeError(
                f"If defined, description must be a string, not {type(description)}"
            )
        if isinstance(icon_path, (str, Path, type(None))):
            self.icon_path = self.check_icon_path(icon_path)
        else:
            raise TypeError(
                f"If defined, icon_path must be a string or pathlib.Path, not {type(icon_path)}"
            )
        if isinstance(work_dir, (str, Path, type(None))):
            self.work_dir = self.check_work_dir(work_dir)
        else:
            raise TypeError(
                f"If defined, work_dir must be a string or pathlib.Path, not {type(work_dir)}"
            )

    def create(
        self,
        desktop: bool = False,
        start_menu: bool = False,
    ) -> tuple[Path | None, Path | None]:
        """Creates shortcuts.

        Args:
            desktop (bool, optional): True to generate a Desktop shortcut. \
                Defaults to False.
            start_menu (bool, optional): True to generate a 'Start Menu' shortcut. \
                Defaults to False.

        Raises:
            TypeError: if options are not booleans

        Returns:
            tuple[Path, Path]: desktop and startmenu path
        """
        if isinstance(desktop, bool):
            self.desktop = desktop
        else:
            raise TypeError(f"'desktop' option must be a boolean, not {type(desktop)}")
        if isinstance(start_menu, bool):
            self.start_menu = start_menu
        else:
            raise TypeError(
                f"'start_menu' option must be a boolean, not {type(start_menu)}"
            )

        if not desktop and not start_menu:
            logger.debug(
                "Shortcut will not be created because both desktop and start "
                "menu options are False."
            )
            return (None, None)

        if opersys == "win32":
            return self.win32_create()
        elif opersys == "linux":
            return self.freedesktop_create()
        else:
            return (None, None)

    def check_exec_arguments(self, exec_arguments: Iterable[str] | None) -> str | None:
        """Check if exec_arguments are valid.

        Args:
            exec_arguments (Iterable[str] | None): input executable arguments to check

        Returns:
            str | None: str of arguments
        """
        if not exec_arguments:
            return None

        # iterate and separate with spaces
        return " ".join(exec_arguments)

    def check_icon_path(self, icon_path: str | Path | None) -> Path | None:
        """Check icon path and return full path if it exists.

        Args:
            icon_path (str | Path | None): input icon path to check

        Returns:
            Path | None: icon path as Path if str or Path, else None
        """
        if icon_path is None:
            logger.debug(
                f"Shortcut '{self.name}' has no icon specified. Fallback to default QGIS icon."
            )
            return self.os_config.shortcut_icon_default_path

        # checks
        if check_path(
            input_path=icon_path,
            must_be_a_file=True,
            must_be_readable=True,
            must_exists=True,
            raise_error=False,
        ):
            return Path(icon_path).resolve()
        else:
            logger.warning(f"Icon does not exist: {icon_path}")
            return None

    def check_work_dir(self, work_dir: str | Path | None) -> Path | None:
        """Check work dir and return full path if it exists.

        Args:
            work_dir (str | Path | None): input work dir to check

        Returns:
            Path | None: work dir as Path if str or Path, else None
        """
        if not work_dir:
            return None
        # store as path
        work_dir = Path(work_dir)
        # checks
        if work_dir.is_dir():
            return work_dir.resolve()
        else:
            logger.warning(f"Work folder does not exist: {work_dir}")
            return None

    # -- PROPERTIES --------------------------------------------------------------
    @property
    def desktop_path(self) -> Path:
        """Return the user Desktop folder.

        Returns:
            Path: path to the current user Desktop folder.
        """
        return get_user_desktop_folder()

    @property
    def homedir_path(self) -> Path | None:
        """Return home directory.

        Returns:
            Path | None: path to the user home
        """
        return get_user_home_folder()

    @property
    def startmenu_path(self) -> Path | None:
        """Return user Start Menu Programs folder.

        Returns:
            Path: path to the Start Menu Programs folder
        """
        return get_user_startmenu_folder()

    # -- PRIVATE --------------------------------------------------------------
    def freedesktop_create(self) -> tuple[Path | None, Path | None]:
        """Creates shortcut on distributions using FreeDesktop.

        Returns:
            tuple[Path | None, Path | None]: desktop and startmenu path
        """
        # grab shortcut template depending if we are in frozen mode
        # (typically PyInstaller) or as "normal" Python
        if not is_running_pyinstaller():
            template_shortcut = Path(__file__).parent / "shortcut_freedesktop.template"
            logger.debug(f"Using shortcut template in Python mode: {template_shortcut}")
        else:
            template_shortcut = Path(getattr(sys, "_MEIPASS", sys.executable)).joinpath(
                "shortcuts/shortcut_freedesktop.template"
            )
            logger.debug(
                f"Using shortcut template in packaged mode: {template_shortcut}"
            )

        if not check_path(
            input_path=template_shortcut,
            must_be_a_file=True,
            must_be_readable=True,
            must_exists=True,
            raise_error=False,
        ):
            logger.error(
                FileNotFoundError(
                    f"Shortcut template ({template_shortcut}) doesn't exist. "
                    "Unable to create shortcuts."
                )
            )
            return (None, None)

        # load template
        with template_shortcut.open("r", encoding="UTF-8") as bf_tpl:
            tpl = Template(bf_tpl.read())

        # handle case where work dir is not defined
        if isinstance(self.work_dir, Path):
            profile_name = self.work_dir.name
            profile_folder = str(self.work_dir)
        else:
            profile_name = "default"
            profile_folder = ""

        # executable path quoted to handle spaces, arguments are already prepared
        exec_line = f'"{escape_freedesktop_exec_quoted(str(self.exec_path))}"'
        if self.exec_arguments:
            exec_line += f" {self.exec_arguments}"

        # subsitute with values
        shortcut_text = tpl.safe_substitute(
            {
                "description": self.description,
                "exec": exec_line,
                "icon_path": self.icon_path,
                "profile_folder_path_key": profile_folder,
                # actions arguments, quoted to handle spaces in paths
                "profile_folder_exec_arg": (
                    f'"{escape_freedesktop_exec_quoted(profile_folder)}"'
                ),
                "profile_folder_shell_arg": escape_freedesktop_exec_quoted(
                    shlex.quote(profile_folder)
                ),
                # profile name within single quotes in a shell command
                "profile_name_shell_quoted": escape_freedesktop_exec_quoted(
                    profile_name.replace("'", "'\\''")
                ),
                "profile_name": profile_name,
                "shortcut_name": self.name,
            }
        )

        # desktop shortcut
        if self.desktop:
            self.desktop_path.mkdir(parents=True, exist_ok=True)

            # create shortcut
            shortcut_desktop_path = Path(
                self.desktop_path,
                f"qdt.{sluggy(profile_name, '.')}.qgis.desktop",
            )
            shortcut_desktop_path.write_text(shortcut_text, encoding="UTF-8")
            shortcut_desktop_path.chmod(
                shortcut_desktop_path.stat().st_mode
                | (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH),
                follow_symlinks=True,
            )
        else:
            shortcut_desktop_path = None

        # create required shortcut
        if self.start_menu and isinstance(self.startmenu_path, Path):
            self.startmenu_path.mkdir(parents=True, exist_ok=True)
            # create shortcut
            shortcut_start_menu_path = Path(
                self.startmenu_path,
                f"qdt.{sluggy(profile_name, '.')}.qgis.desktop",
            )
            shortcut_start_menu_path.write_text(shortcut_text, encoding="UTF-8")
            shortcut_start_menu_path.chmod(
                shortcut_start_menu_path.stat().st_mode
                | (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH),
                follow_symlinks=True,
            )
        else:
            shortcut_start_menu_path = None

        return (shortcut_desktop_path, shortcut_start_menu_path)

    def win32_create(self) -> tuple[Path | None, Path | None]:
        """Creates shortcut on Windows.

        Returns:
            tuple[Path | None, Path | None]: desktop and startmenu path
        """
        # variable
        _WSHELL = win32com.client.Dispatch("Wscript.Shell", pythoncom.CoInitialize())  # noqa: N806

        # desktop shortcut
        if self.desktop:
            shortcut_desktop_path = (
                self.desktop_path / f"{self.name}{self.os_config.shortcut_extension}"
            )

            wscript = _WSHELL.CreateShortCut(str(shortcut_desktop_path.resolve()))
            if self.exec_arguments:
                wscript.Arguments = self.exec_arguments
            wscript.Targetpath = str(self.exec_path.resolve())
            if self.work_dir:
                wscript.WorkingDirectory = str(self.work_dir.resolve())
            wscript.WindowStyle = 0
            if self.description:
                wscript.Description = self.description
            else:
                wscript.Description = (
                    QDT_SHORTCUT_DESCRIPTION_PREFIX + f" {__version__}"
                )
            if self.icon_path:
                if isinstance(self.icon_path, Path):
                    wscript.IconLocation = str(self.icon_path.resolve())
                elif isinstance(self.icon_path, str):
                    wscript.IconLocation = self.icon_path
                else:
                    logger.warning(
                        f"Bad icon path type: {type(self.icon_path)} != (Path, str)."
                    )
            try:
                wscript.save()
            except PermissionError as err:
                logger.error(
                    f"Permission error when creating desktop shortcut at "
                    f"{shortcut_desktop_path}. Trace: {err}"
                )

                shortcut_desktop_path = None

        else:
            shortcut_desktop_path = None

        # start menu shortcut
        if self.start_menu and isinstance(self.startmenu_path, Path):
            shortcut_start_menu_path = (
                self.startmenu_path / f"{self.name}{self.os_config.shortcut_extension}"
            )

            wscript = _WSHELL.CreateShortCut(str(shortcut_start_menu_path.resolve()))
            if self.exec_arguments:
                wscript.Arguments = self.exec_arguments
            wscript.Targetpath = str(self.exec_path.resolve())
            if self.work_dir is not None:
                wscript.WorkingDirectory = str(self.work_dir.resolve())
            wscript.WindowStyle = 0
            if self.description:
                wscript.Description = self.description
            else:
                wscript.Description = (
                    QDT_SHORTCUT_DESCRIPTION_PREFIX + f" {__version__}"
                )
            if self.icon_path is not None:
                wscript.IconLocation = str(self.icon_path.resolve())
            try:
                wscript.save()
            except PermissionError as err:
                logger.error(
                    f"Permission error when creating start menu shortcut at "
                    f"{shortcut_start_menu_path}. Trace: {err}"
                )

                shortcut_start_menu_path = None
        else:
            shortcut_start_menu_path = None

        return (shortcut_desktop_path, shortcut_start_menu_path)
