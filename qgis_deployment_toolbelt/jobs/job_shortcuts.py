#! python3  # noqa: E265

"""Manage application shortcuts on end-user machine.

Author: Julien Moura (https://github.com/guts)
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from pathlib import Path
from sys import platform as opersys

# package
from qgis_deployment_toolbelt.__about__ import __title__, __version__
from qgis_deployment_toolbelt.jobs.generic_job import GenericJob
from qgis_deployment_toolbelt.profiles.qdt_profile import QdtProfile
from qgis_deployment_toolbelt.shortcuts.shortcuts_handler import ApplicationShortcut


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Classes ###############
# ##################################


class JobShortcutsManager(GenericJob):
    """Job to create or remove shortcuts on end-user machine."""

    ID: str = "shortcuts-manager"
    OPTIONS_SCHEMA: dict = {
        "action": {
            "type": str,
            "required": False,
            "default": "create_or_restore",
            "possible_values": ("create", "create_or_restore", "remove"),
            "condition": "in",
        },
        "include": {
            "type": (list, str),
            "required": False,
            "default": None,
            "possible_values": None,
            "condition": None,
            "sub_options": {
                "additional_arguments": {
                    "type": list[str] | str,
                    "required": False,
                    "default": None,
                    "possible_values": None,
                    "condition": None,
                },
                "desktop": {
                    "type": bool,
                    "required": False,
                    "default": False,
                    "possible_values": None,
                    "condition": None,
                },
                "icon": {
                    "type": str,
                    "required": False,
                    "default": None,
                    "possible_values": None,
                    "condition": None,
                },
                "label": {
                    "type": str,
                    "required": False,
                    "default": "QGIS",
                    "possible_values": None,
                    "condition": None,
                },
                "profile": {
                    "type": str,
                    "required": True,
                    "default": None,
                    "possible_values": None,
                    "condition": None,
                },
                "start_menu": {
                    "type": bool,
                    "required": False,
                    "default": True,
                    "possible_values": None,
                    "condition": None,
                },
            },
        },
    }
    SHORTCUTS_CREATED: list = []
    SHORTCUTS_REMOVED: list = []

    def __init__(self, options: dict) -> None:
        """Instantiate the class.

        :param dict options: profiles source (remote, can be a local network) and
            destination (local).
        """
        super().__init__()
        self.options: dict = self.validate_options(options)

    def run(self) -> None:
        """Execute job logic."""
        # check of there are some profiles folders within the downloaded folder
        downloaded_profiles = self.list_downloaded_profiles()
        if downloaded_profiles is None:
            logger.error("No QGIS profile found in the downloaded folder.")
            return

        # check action
        if self.options.get("action") in ("create", "create_or_restore"):
            for inc_shortcut in self.options.get("include", []):
                qdt_profile = self.get_matching_profile_from_name(
                    li_profiles=downloaded_profiles,
                    profile_name=inc_shortcut.get("profile"),
                )
                if not qdt_profile:
                    continue

                # instanciate shortcut
                shortcut = ApplicationShortcut(
                    name=inc_shortcut.get("label"),
                    exec_path=self.os_config.get_qgis_bin_path(),
                    description=f"Created with {__title__} {__version__}",
                    icon_path=self._get_icon_path(
                        profile=qdt_profile, icon_filename=inc_shortcut.get("profile")
                    ),
                    exec_arguments=self._get_arguments_ready(
                        inc_shortcut.get("profile"),
                        inc_shortcut.get("additional_arguments"),
                    ),
                    work_dir=qdt_profile.path_in_qgis,
                )
                shortcut.create(
                    desktop=inc_shortcut.get("desktop", False),
                    start_menu=inc_shortcut.get("start_menu", True),
                )
                logger.info(f"Created shortcut {shortcut.name}")
                self.SHORTCUTS_CREATED.append(shortcut)

            logger.debug(f"Job {self.ID} ran successfully.")
        else:
            raise NotImplementedError

    # -- INTERNAL LOGIC ------------------------------------------------------
    def _pick_compatible_icon_for_os(self, icon_path: Path) -> Path:
        """Return the most suitable icon path for the current OS.

        Strategy (in order):
        1. If the icon's extension is already preferred for this OS, return it as-is.
        2. Look for a sibling file with the same stem but a preferred extension.
        3. Convert the icon on-the-fly to the top-priority format for this OS.

        Args:
            icon_path (Path): resolved path to the icon found on disk.

        Returns:
            Path: path to an icon in the OS-preferred format.
        """
        preferred_exts = tuple(
            f".{e.lstrip('.')}" for e in (self.os_config.shortcut_icon_extensions or ())
        )

        current_ext = icon_path.suffix.lower()

        # 1. Already the right format
        if current_ext in preferred_exts:
            logger.debug(
                f"{current_ext} is already one of the accepter formats for OS '{opersys}'. "
                f"Let's use {icon_path}."
            )
            return icon_path

        # 2. Sibling file with a preferred extension
        for ext in preferred_exts:
            sibling = icon_path.with_suffix(ext)
            if sibling.is_file():
                logger.debug(
                    f"OS-preferred icon sibling found ({ext}), using it instead of "
                    f"{current_ext}: {sibling}"
                )
                return sibling

        # not found, using original file
        top_preferred = preferred_exts[0]
        logger.debug(
            f"No {top_preferred} icon found alongside {icon_path.name}. "
            "Using original file."
        )

        return icon_path

    def _get_icon_path(self, profile: QdtProfile, icon_filename: str) -> Path | None:
        """Get icon path to use with the shortcut. Looking for:

            1. checks if an icon key has been specified in the profile.json file and
                if it exists
            2. checks if an icon has been specified into scenario and if it exists
                within profile folder (in QGIS)
            3. checks if an icon has been specified into scenario and if it exists under
                a subfolder starting from the toolbelt (and handling pathlib OSError)

        Args:
            profile (QdtProfile): QGIS profile object
            icon_filename (str): icon path as mentioned into the scenario file

        Returns:
            Path: icon path as Path if str or Path, else None
        """
        profile_icon_installed = None

        # 1. check icon specified in profile.json
        if profile.icon:
            profile_icon_installed = profile.path_in_qgis.joinpath(profile.icon)
            if profile_icon_installed.is_file():
                logger.debug(
                    f"Icon set in profile.json exists so it will be used: {profile_icon_installed}"
                )
                return self._pick_compatible_icon_for_os(
                    profile_icon_installed.resolve()
                )

        # if not specified in profile.json nor in scenario --> None
        if icon_filename is None:
            logger.debug("No icon found in profile.json nor in scenario.")
            return None

        # 2. check if icon specified in scenario exists in profile folder
        try:
            li_icons_sub_profile_folder = list(
                profile.path_in_qgis.rglob(f"{icon_filename}")
            )
            if len(li_icons_sub_profile_folder):
                logger.debug(
                    "Icon found under the installed profile folder: "
                    f"{li_icons_sub_profile_folder[0].resolve()}"
                )
                return self._pick_compatible_icon_for_os(
                    li_icons_sub_profile_folder[0].resolve()
                )

        except OSError as err:
            logger.error(
                f"Looking for icon into profile subfolder failed. Trace: {err}"
            )

        # 3. check if icon specified in scenario exists under QDT
        try:
            li_icons_sub_qdt_folder = list(Path().glob(f"{icon_filename}"))
            if len(li_icons_sub_qdt_folder):
                logger.debug(
                    f"Icon found under the QDT folder: {li_icons_sub_qdt_folder[0].resolve()}"
                )
                return self._pick_compatible_icon_for_os(
                    li_icons_sub_qdt_folder[0].resolve()
                )

        except OSError as err:
            logger.error(
                f"Looking for icon into profile subfolder failed. Trace: {err}"
            )

        return profile_icon_installed

    def _get_arguments_ready(
        self, profile: str, in_arguments: list[str] | str | None = None
    ) -> list[str]:
        """Prepare arguments for the executable shortcut.

        Args:
            profile (str): profile's name
            in_arguments (list[str] | str | None, optional): argument as defined in the
                scenario file. Defaults to None.

        Raises:
            TypeError: if arguments are not str or list of str

        Returns:
            list[str]: tuple of strings separated by spaces
        """
        # add profile name
        arguments: list = ["--profile", f'"{profile}"']

        # add additional arguments
        if in_arguments:
            if isinstance(in_arguments, str):
                logger.warning(
                    "Additional arguments should be a list of strings, not a single string. "
                    "We will try to split it by spaces."
                )
                in_arguments = in_arguments.split(" ")
            elif isinstance(in_arguments, list):
                in_arguments = [
                    str(arg)
                    for arg in in_arguments
                    if isinstance(arg, (str, int, float))
                ]
            elif not isinstance(in_arguments, (list, str)):
                raise TypeError(
                    f"Additional arguments should be a string or a list of strings, not {type(in_arguments)}"
                )
            arguments.extend(in_arguments)

        return arguments
