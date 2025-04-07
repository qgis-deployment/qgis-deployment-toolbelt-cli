#! python3  # noqa: E265

"""
Define toolbelt constant types and values.

Author: Julien Moura (https://github.com/guts)
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# special
from __future__ import annotations

# Standard library
import ast
import logging
import re
from dataclasses import dataclass
from os import PathLike, getenv
from os.path import expanduser, expandvars
from pathlib import Path
from shutil import which
from sys import platform as opersys

# package
from qgis_deployment_toolbelt.utils.check_path import check_path

# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)

# defaults
DEFAULT_QDT_WORKING_FOLDER = Path.home().joinpath(".cache/qgis-deployment-toolbelt")

# QGIS executable filenames
QGIS_BIN_WINDOWS_FILENAME: str = "qgis-bin.exe"
QGIS_LTR_BIN_WINDOWS_FILENAME: str = "qgis-ltr-bin.exe"

# Operating systems
SUPPORTED_OPERATING_SYSTEMS_CODENAMES: tuple[str, ...] = ("darwin", "linux", "win32")

# regex
RE_QGIS_FINDER_DIR = re.compile(r"QGIS (\d+)\.(\d+)\.(\d+)", re.IGNORECASE)
RE_QGIS_FINDER_VERSION = re.compile(r"QGIS (\d+\.\d+\.\d+)-(\w+).*")

# #############################################################################
# ########## Functions #############
# ##################################


def get_qdt_logs_folder() -> Path:
    """Get QDT logs folder. It uses the default path (a `logs` subfolder under the QDT
        working folder) or the path defined in environment variable `QDT_LOGS_DIR`.

    Returns:
        Path: path to the QDT logs folder.
    """
    # default
    qdt_logs_folder = get_qdt_working_directory().joinpath("logs")

    if isinstance(getenv("QDT_LOGS_DIR"), str):
        qdt_logs_folder_env = Path(expandvars(expanduser(getenv("QDT_LOGS_DIR"))))
        logger.debug(
            f"Logs folder set from QDT_LOGS_DIR environment variable: {qdt_logs_folder_env}"
        )
        # check
        if not check_path(
            input_path=qdt_logs_folder_env,
            must_be_a_file=False,
            must_be_a_folder=True,
            must_be_writable=True,
            raise_error=False,
        ):
            logger.error(
                "Logs folder path set in QDT_LOGS_DIR environment variable is not a "
                f"valid folder path: {qdt_logs_folder_env}. It must to point to a "
                f"writable folder. Fallback to default {qdt_logs_folder}."
            )
        else:
            qdt_logs_folder = qdt_logs_folder_env
    else:
        logger.debug(f"Default value used for QDT logs folder: {qdt_logs_folder}")

    return qdt_logs_folder


def get_qdt_working_directory(
    specific_value: PathLike | None = None, identifier: str | None = None
) -> Path:
    """Get QDT working directory.

    Args:
        specific_value (PathLike, optional): a specific path to use. If set it's \
            expanded and returned. Defaults to None.
        identifier (str, optional): used to make the folder unique. Defaults to None.

    Returns:
        Path: path to the QDT working directory
    """
    if specific_value:
        logger.debug(
            f"QDT working folder - Using the specified value: {specific_value}"
        )
        return Path(expandvars(expanduser(specific_value)))
    elif qdt_local_working_folder := getenv("QDT_LOCAL_WORK_DIR"):
        logger.debug(
            "QDT working folder - Using value specified as environment variable: "
            f"{qdt_local_working_folder}"
        )
        return Path(expandvars(expanduser(qdt_local_working_folder)))
    else:
        if identifier is not None:
            logger.debug(
                f"QDT working folder - Using default path '{DEFAULT_QDT_WORKING_FOLDER}' "
                f"with custom identifier '{identifier}'"
            )
            return Path(
                expandvars(
                    expanduser(
                        getenv(
                            "QDT_LOCAL_WORK_DIR",
                            DEFAULT_QDT_WORKING_FOLDER.joinpath(identifier),
                        ),
                    )
                )
            )
        else:
            logger.debug(
                f"QDT working folder - Using default path: {DEFAULT_QDT_WORKING_FOLDER}"
            )
            return Path(
                expandvars(
                    expanduser(getenv("QDT_LOCAL_WORK_DIR", DEFAULT_QDT_WORKING_FOLDER))
                )
            )


# #############################################################################
# ########## Classes ###############
# ##################################


@dataclass
class OSConfiguration:
    """Settings related to QGIS and depending on operating system"""

    name_python: str
    names_alter: list[str]
    qgis_bin_exe_path: Path | None = None
    qgis_profiles_path: Path | None = None
    shortcut_extension: str | None = None
    shortcut_forbidden_chars: tuple[str, ...] | None = None
    shortcut_icon_extensions: tuple[str, ...] | None = None
    shortcut_icon_default_path: str | None = None

    @property
    def get_qgis_bin_path(self) -> Path:
        """Returns the QGIS path determined from QDT_QGIS_EXE_PATH environment variable,
        or result of which command or fallback to default value passed to the object.

        Returns:
            Path: path to the QGIS bin/exe
        """
        if envvar := getenv("QDT_QGIS_EXE_PATH"):
            if envvar.startswith("{") and envvar.endswith("}"):
                try:
                    qdt_qgis_exe_path = ast.literal_eval(envvar)
                    if isinstance(qdt_qgis_exe_path, dict):
                        logger.debug(
                            f"'QDT_QGIS_EXE_PATH' is a valid dictionary: {envvar}"
                        )
                        for k, v in qdt_qgis_exe_path.items():
                            if k in self.names_alter + [self.name_python]:
                                logger.debug(
                                    f"QGIS path found in 'QDT_QGIS_EXE_PATH' dictionary: {v}"
                                )
                                return Path(expandvars(expanduser(v)))
                except Exception as err:
                    logger.error(
                        f"Failed to interpret 'QDT_QGIS_EXE_PATH' value: {envvar}."
                        f"Trace: {err}"
                    )
            elif check_path(
                input_path=envvar,
                must_exists=False,
                must_be_readable=False,
                raise_error=False,
            ):
                logger.debug(
                    f"'QDT_QGIS_EXE_PATH' is a simple string and a valid path: {envvar}"
                )
                return Path(expandvars(expanduser(envvar)))

            # fallback
            logger.warning(
                f"Unrecognised value format for 'QDT_QGIS_EXE_PATH': {envvar}. "
                "Fallback to default path: "
                f"{Path(expandvars(expanduser(self.qgis_bin_exe_path)))}"
            )
            return Path(expandvars(expanduser(self.qgis_bin_exe_path)))
        elif which_qgis_path := which("qgis"):
            logger.debug(f"QGIS path found using which: {which_qgis_path}")
            return Path(which_qgis_path)
        else:
            logger.debug(
                f"QGIS path not found, using default value: {self.qgis_bin_exe_path}"
            )
            return Path(expandvars(expanduser(self.qgis_bin_exe_path)))

    def valid_shortcut_name(self, shortcut_name: str) -> bool:
        """Check if a given string is a valid shortcut name for the current operating
        system.

        Args:
            shortcut_name (str): given shortcut name to check

        Returns:
            bool: True if the givn string can be used as shortcut name
        """
        if self.shortcut_forbidden_chars is None:
            return True
        for char in self.shortcut_forbidden_chars:
            if char in shortcut_name:
                logger.error(
                    f"Shortcut name '{shortcut_name}' contains forbidden char '{char}'"
                )
                return False
        return True

    @classmethod
    def from_opersys(
        cls,
        operating_system_codename: str | None = None,
    ) -> OSConfiguration:
        """Create configuration object with defaults values from a operating system
            code name.

        Args:
            operating_system_codename: operating system code name as specified in \
                sys.platform. If None, fallback to current operating system. \
                    Defaults to None.

        Returns:
            Self: OSConfiguration object with defaults settings
        """
        # if not specified, fallback to current operating system
        if operating_system_codename is None:
            operating_system_codename = opersys
            logger.debug(
                f"Getting configuration for current operating system: {opersys}"
            )

        # returning configuration for operating system
        if operating_system_codename == "darwin":
            return cls(
                name_python="darwin",
                names_alter=["apple", "mac", "macos"],
                qgis_bin_exe_path=Path("/usr/bin/qgis"),
                qgis_profiles_path=Path(
                    getenv(
                        "QGIS_CUSTOM_CONFIG_PATH",
                        Path.home()
                        / "Library/Application Support/QGIS/QGIS3/profiles/",
                    )
                ),
                shortcut_extension="app",
                shortcut_icon_extensions=("icns",),
            )
        elif operating_system_codename == "linux":
            return cls(
                name_python="linux",
                names_alter=["kubuntu", "ubuntu"],
                qgis_bin_exe_path=Path("/usr/bin/qgis"),
                qgis_profiles_path=Path(
                    getenv(
                        "QGIS_CUSTOM_CONFIG_PATH",
                        Path.home() / ".local/share/QGIS/QGIS3/profiles/",
                    )
                ),
                shortcut_extension=".desktop",
                shortcut_icon_extensions=("ico", "svg", "png"),
                shortcut_icon_default_path="qgis",
            )
        elif operating_system_codename == "win32":
            return cls(
                name_python="win32",
                names_alter=["win", "windows"],
                qgis_bin_exe_path=Path(
                    expandvars(
                        expanduser("%PROGRAMFILES%/QGIS 3.34.4/bin/qgis-ltr-bin.exe")
                    )
                ),
                qgis_profiles_path=Path(
                    getenv(
                        "QGIS_CUSTOM_CONFIG_PATH",
                        expandvars("%APPDATA%/QGIS/QGIS3/profiles"),
                    )
                ),
                shortcut_extension=".lnk",
                shortcut_forbidden_chars=("<", ">", ":", '"', "/", "\\", "|", "?", "*"),
                shortcut_icon_extensions=("ico",),
            )
        else:
            raise ValueError(
                f"Unsupported operating system specified: {operating_system_codename}. "
                "Must be one of: {', '.join('darwin', 'linux', 'win32')}"
            )
