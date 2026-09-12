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
from shutil import ignore_patterns, which
from sys import platform as opersys
from typing import TYPE_CHECKING, Literal, cast, get_args

# 3rd party
from packaging.version import InvalidVersion, Version

# package
from qgis_deployment_toolbelt.utils.check_path import check_path


if TYPE_CHECKING:
    from collections.abc import Callable


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)

# defaults
CleanupScopes = Literal["plugins_cache", "plugins_installed"]
DEFAULT_CLEANUP_SCOPES: list[CleanupScopes] = ["plugins_cache"]

DeletionPolicy = Literal["force_delete", "trash_only", "trash_or_delete"]
DEFAULT_DELETION_POLICY: DeletionPolicy = "trash_or_delete"

DEFAULT_QDT_WORKING_FOLDER = Path.home().joinpath(".cache/qgis-deployment-toolbelt")

# QGIS major versions supported by QDT
SupportedQgisMajorVersion = Literal[3, 4]
# fallback used when the QGIS major version can't be determined
DEFAULT_QGIS_MAJOR_VERSION: SupportedQgisMajorVersion = 3

MANAGED_PLUGINS_MANIFEST_FILENAME: str = ".qdt-managed-plugins.json"

# files to ignore when copying profiles. TODO: make it configurable?
COPY_IGNORED_PATTERNS: Callable = ignore_patterns("*.lnk", "thumbs.db", ".DS_Store")

# environment variables
ENV_VAR_QGIS_EXE_PATH: str = "QDT_QGIS_EXE_PATH"
ENV_VAR_QGIS_VERSION: str = "QDT_QGIS_VERSION"

# QGIS executable filenames
QGIS_BIN_WINDOWS_FILENAME: str = "qgis-bin.exe"
QGIS_LTR_BIN_WINDOWS_FILENAME: str = "qgis-ltr-bin.exe"

# QGIS configuration files stored under `<profile>/QGIS/`.
# the settings file is named after the QGIS major version: QGIS3.ini, QGIS4.ini...
# TODO: QDT only handles the ini file so far, so customization changes it writes are
# ignored by QGIS 4 as soon as QGIS 4 has written its own XML file.
QGIS_PROFILE_CUSTOMIZATION_INI_FILENAME: str = "QGISCUSTOMIZATION3.ini"
QGIS_PROFILE_CUSTOMIZATION_XML_FILENAME: str = "QGISCUSTOMIZATION.xml"

# maximum time (in seconds) allowed to a QGIS binary to answer to `--version`
QGIS_VERSION_LOOKUP_TIMEOUT_SECONDS: int = int(
    getenv("QDT_QGIS_VERSION_LOOKUP_TIMEOUT_SECONDS", 20)
)

# Operating systems
SUPPORTED_OPERATING_SYSTEMS_CODENAMES: tuple[str, ...] = ("darwin", "linux", "win32")

# regex
RE_QGIS_FINDER_DIR = re.compile(r"QGIS (\d+)\.(\d+)\.(\d+)", re.IGNORECASE)
RE_QGIS_FINDER_VERSION = re.compile(r"QGIS (\d+\.\d+\.\d+)-(\w+).*")
RE_QGIS_PROFILE_INI_STEM = re.compile(r"^QGIS(\d+)$", re.IGNORECASE)
RE_QGIS_VERSIONED_FOLDER = re.compile(r"^QGIS(\d+)$", re.IGNORECASE)

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
        qdt_logs_folder_env = Path(expandvars(expanduser(getenv("QDT_LOGS_DIR"))))  # noqa: PTH111
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
        return Path(expandvars(expanduser(specific_value)))  # noqa: PTH111
    elif qdt_local_working_folder := getenv("QDT_LOCAL_WORK_DIR"):
        logger.debug(
            "QDT working folder - Using value specified as environment variable: "
            f"{qdt_local_working_folder}"
        )
        return Path(expandvars(expanduser(qdt_local_working_folder)))  # noqa: PTH111
    else:
        if identifier is not None:
            logger.debug(
                f"QDT working folder - Using default path '{DEFAULT_QDT_WORKING_FOLDER}' "
                f"with custom identifier '{identifier}'"
            )
            return Path(
                expandvars(
                    expanduser(  # noqa: PTH111
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
                )  # noqa: PTH111
            )


def get_qgis_version_major(
    qgis_version: str | int | None = None,
) -> SupportedQgisMajorVersion:
    """Determine the QGIS major version QDT has to work with .

    Args:
        qgis_version (str | int | None, optional): QGIS version to read the major \
            version from. Anything `packaging` can parse is accepted. If None, the \
            `QDT_QGIS_VERSION` environment variable (set by the job
            `qgis-installation-finder`) is used. Defaults to None.

    Returns:
        SupportedQgisMajorVersion: QGIS major version supported by QDT. Fallback to
            `DEFAULT_QGIS_MAJOR_VERSION` when it can't be determined.
    """
    if qgis_version is None:
        qgis_version = getenv(ENV_VAR_QGIS_VERSION)

    if qgis_version is None:
        logger.debug(
            f"'{ENV_VAR_QGIS_VERSION}' is not set and no QGIS version has been passed, "
            f"so QDT considers it works with QGIS {DEFAULT_QGIS_MAJOR_VERSION}. Run the "
            "'qgis-installation-finder' job before the others to make QDT aware of the "
            "installed QGIS version."
        )
        return DEFAULT_QGIS_MAJOR_VERSION

    try:
        version_major = Version(str(qgis_version)).major
    except InvalidVersion:
        logger.warning(
            f"Unable to extract a QGIS major version from '{qgis_version}': it uses an "
            "incompatible versioning scheme. See https://peps.python.org/pep-0440/. "
            f"Fallback to QGIS {DEFAULT_QGIS_MAJOR_VERSION}."
        )
        return DEFAULT_QGIS_MAJOR_VERSION

    if version_major not in get_args(SupportedQgisMajorVersion):
        logger.warning(
            f"QGIS {version_major} (from '{qgis_version}') is not supported by QDT. "
            "Supported major versions: "
            f"{', '.join(map(str, get_args(SupportedQgisMajorVersion)))}. "
            f"Fallback to QGIS {DEFAULT_QGIS_MAJOR_VERSION}."
        )
        return DEFAULT_QGIS_MAJOR_VERSION

    return cast("SupportedQgisMajorVersion", version_major)


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
    qgis_user_data_path: Path | None = None
    qgis_version_major: SupportedQgisMajorVersion = DEFAULT_QGIS_MAJOR_VERSION
    shortcut_extension: str | None = None
    shortcut_forbidden_chars: tuple[str, ...] | None = None
    shortcut_icon_default_path: str | None = None
    shortcut_icon_extensions: tuple[str, ...] | None = None

    @property
    def qgis_profile_ini_filename(self) -> str:
        """Filename of the QGIS settings file stored in a profile `QGIS` subfolder.

        Returns:
            str: name of the profile settings ini file.
        """
        return f"QGIS{self.qgis_version_major}.ini"

    def get_qgis_profiles_path(
        self, qgis_version_major: SupportedQgisMajorVersion | None = None
    ) -> Path:
        """Get the folder where QGIS stores the user's profiles.

        The `QGIS_CUSTOM_CONFIG_PATH` environment variable, used also by QGIS itself,
        takes precedence and is used as is.

        Args:
            qgis_version_major (SupportedQgisMajorVersion | None, optional): QGIS major
                version to build the path for. If None, the one stored on the object is
                used. Defaults to None.

        Returns:
            Path: path to the QGIS profiles folder.
        """
        if custom_config_path := getenv("QGIS_CUSTOM_CONFIG_PATH"):
            return Path(custom_config_path)

        if qgis_version_major is None:
            qgis_version_major = self.qgis_version_major

        return self.qgis_user_data_path.joinpath(
            f"QGIS{qgis_version_major}", "profiles"
        )

    def _is_envvar_qgis_exe_path_a_dict(self) -> bool:
        """Check if the QDT_QGIS_EXE_PATH environment variable is a dictionary.

        Returns:
            bool: True if the environment variable is a dictionary, False otherwise.
        """
        if envvar := getenv("QDT_QGIS_EXE_PATH"):
            if envvar.startswith("{") and envvar.endswith("}"):
                try:
                    qdt_qgis_exe_path = ast.literal_eval(envvar)
                    if isinstance(qdt_qgis_exe_path, dict):
                        logger.debug(
                            f"'QDT_QGIS_EXE_PATH' is a valid dictionary: {envvar}"
                        )
                        return True
                except Exception as err:
                    logger.info(
                        f"Failed to interpret 'QDT_QGIS_EXE_PATH' value: {envvar}. "
                        f"Trace: {err}"
                    )
        return False

    def _is_envvar_qgis_exe_path_a_string(self) -> bool:
        """Check if the QDT_QGIS_EXE_PATH environment variable is a string.

        Returns:
            bool: True if the environment variable is a string, False otherwise.
        """
        if isinstance(getenv("QDT_QGIS_EXE_PATH"), str):
            return check_path(
                input_path=getenv("QDT_QGIS_EXE_PATH"),
                must_exists=False,
                must_be_readable=False,
                raise_error=False,
            )
        return False

    def get_qgis_bin_path(self, use_fallback: bool = True) -> bool | Path:
        """Returns the QGIS path determined from QDT_QGIS_EXE_PATH environment variable,
        or result of which command or fallback to default value passed to the object.

        Returns:
            Path: path to the QGIS bin/exe
        """
        if envvar := getenv("QDT_QGIS_EXE_PATH"):
            if self._is_envvar_qgis_exe_path_a_dict():
                try:
                    for k, v in ast.literal_eval(envvar).items():
                        if k in self.names_alter + [self.name_python]:
                            logger.debug(
                                f"QGIS path found in 'QDT_QGIS_EXE_PATH' dictionary: {v}"
                            )
                            return Path(expandvars(expanduser(v)))  # noqa: PTH111
                except Exception as err:
                    logger.error(
                        f"Failed to use 'QDT_QGIS_EXE_PATH' dict value: {envvar}. "
                        f"Trace: {err}"
                    )
            elif self._is_envvar_qgis_exe_path_a_string():
                logger.debug(
                    f"'QDT_QGIS_EXE_PATH' is a simple string and a valid path: {envvar}"
                )
                return Path(expandvars(expanduser(envvar)))  # noqa: PTH111

            if not use_fallback:
                logger.info(
                    "Environment variable 'QDT_QGIS_EXE_PATH' is set but no valid path "
                    "found. No fallback as requested, returning False."
                )
                return False

            # fallback
            logger.warning(
                f"Unrecognized value format for 'QDT_QGIS_EXE_PATH': {envvar}. "
                "Fallback to default path: "
                f"{Path(expandvars(expanduser(self.qgis_bin_exe_path)))}"  # noqa: PTH111
            )
            return Path(expandvars(expanduser(self.qgis_bin_exe_path)))  # noqa: PTH111

        # not defined in environment variable
        logger.debug("Environment variable 'QDT_QGIS_EXE_PATH' is not set.")
        if not use_fallback:
            logger.info("No fallback as requested, returning False for QGIS exe path.")
            return False

        # fallback to which or default
        if which_qgis_path := which("qgis"):
            logger.debug(f"QGIS path found using which: {which_qgis_path}")
            return Path(which_qgis_path)
        else:
            logger.debug(
                "which command did not find QGIS executable. "
                f"Using default value: {self.qgis_bin_exe_path}"
            )
            return Path(expandvars(expanduser(self.qgis_bin_exe_path)))  # noqa: PTH111

    def valid_shortcut_name(self, shortcut_name: str) -> bool:
        """Check if a given string is a valid shortcut name for the current operating
        system.

        Args:
            shortcut_name (str): given shortcut name to check

        Returns:
            bool: True if the given string can be used as shortcut name
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
        qgis_version_major: SupportedQgisMajorVersion | None = None,
    ) -> OSConfiguration:
        """Create configuration object with defaults values from a operating system
            code name.

        Args:
            operating_system_codename: operating system code name as specified in \
                sys.platform. If None, fallback to current operating system. \
                    Defaults to None.
            qgis_version_major: QGIS major version to target, which determines the \
                profiles folder path. If None, it's the `QDT_QGIS_VERSION` \
                environment variable set by the `qgis-installation-finder` job. \
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

        # if not specified, deduce it from the installed QGIS found by QDT
        if qgis_version_major is None:
            qgis_version_major = get_qgis_version_major()

        # returning configuration for operating system
        if operating_system_codename == "darwin":
            os_config = cls(
                name_python="darwin",
                names_alter=["apple", "mac", "macos"],
                qgis_bin_exe_path=Path("/usr/bin/qgis"),
                qgis_user_data_path=Path.home() / "Library/Application Support/QGIS",
                qgis_version_major=qgis_version_major,
                shortcut_extension="app",
                shortcut_icon_extensions=("icns",),
            )
        elif operating_system_codename == "linux":
            os_config = cls(
                name_python="linux",
                names_alter=["kubuntu", "ubuntu"],
                qgis_bin_exe_path=Path("/usr/bin/qgis"),
                qgis_user_data_path=Path.home() / ".local/share/QGIS",
                qgis_version_major=qgis_version_major,
                shortcut_extension=".desktop",
                shortcut_icon_extensions=("png", "svg"),
                shortcut_icon_default_path="qgis",
            )
        elif operating_system_codename == "win32":
            os_config = cls(
                name_python="win32",
                names_alter=["win", "windows"],
                qgis_bin_exe_path=Path(
                    expandvars("%PROGRAMFILES%/QGIS 3.40.11/bin/qgis-ltr-bin.exe")
                ),
                qgis_user_data_path=Path(expandvars("%APPDATA%/QGIS")),
                qgis_version_major=qgis_version_major,
                shortcut_extension=".lnk",
                shortcut_forbidden_chars=("<", ">", ":", '"', "/", "\\", "|", "?", "*"),
                shortcut_icon_extensions=("ico",),
            )
        else:
            raise ValueError(
                f"Unsupported operating system specified: {operating_system_codename}. "
                f"Must be one of: {', '.join(['darwin', 'linux', 'win32'])}"
            )

        os_config.qgis_profiles_path = os_config.get_qgis_profiles_path()
        logger.debug(
            f"QGIS {qgis_version_major} profiles folder: {os_config.qgis_profiles_path}"
        )

        return os_config
