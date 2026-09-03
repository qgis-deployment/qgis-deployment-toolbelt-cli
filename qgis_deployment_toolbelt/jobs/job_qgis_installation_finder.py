#! python3  # noqa: E265

"""
Tools to find installed QGIS version

Author: Jean-Marie KERLOCH (https://github.com/jmkerloch)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
import os
import subprocess
from os import environ, getenv
from os.path import expanduser, expandvars
from pathlib import Path
from shutil import which
from sys import platform as opersys

# 3rd party
from packaging.version import InvalidVersion, Version

# package
from qgis_deployment_toolbelt.constants import (
    ENV_VAR_QGIS_EXE_PATH,
    ENV_VAR_QGIS_VERSION,
    QGIS_VERSION_LOOKUP_TIMEOUT_SECONDS,
    RE_QGIS_FINDER_DIR,
    RE_QGIS_FINDER_VERSION,
)
from qgis_deployment_toolbelt.exceptions import QgisInstallNotFoundError
from qgis_deployment_toolbelt.jobs.generic_job import GenericJob
from qgis_deployment_toolbelt.utils.check_path import check_path_exists


# #############################################################################
# ########## Globals ###############
# ##################################


# logs
logger = logging.getLogger(__name__)

# #############################################################################
# ########## Classes ###############
# ##################################


class JobQgisInstallationFinder(GenericJob):
    """
    Class to find installed QGIS version
    """

    ID: str = "qgis-installation-finder"

    # -- CACHE --
    CACHE_DETECTED_QGIS_VERSION: str | None = None

    OPTIONS_SCHEMA: dict = {
        "if_not_found": {
            "type": str,
            "required": False,
            "default": "warning",
            "possible_values": ("warning", "error"),
            "condition": "in",
        },
        "version_priority": {
            "type": (list, str),
            "required": False,
            "default": None,
            "possible_values": None,
            "condition": None,
        },
        "search_paths": {
            "type": (list, str),
            "required": False,
            "default": (
                expandvars("%PROGRAMFILES%"),
                expandvars(
                    expanduser(getenv("QDT_OSGEO4W_INSTALL_DIR", "C:\\OSGeo4W"))
                ),  # noqa: PTH111
            ),
            "possible_values": None,
            "condition": None,
        },
    }

    def __init__(self, options: dict) -> None:
        """Instantiate the class.

        Args:
            options (dict): job options
        """

        super().__init__()
        self.options: dict = self.validate_options(options)

    def run(self) -> None:
        """Define QDT_QGIS_EXE_PATH and QDT_QGIS_VERSION for version-dependent jobs,
        like Shortcuts manager.
        """
        if not self.run_needed():
            if self.CACHE_DETECTED_QGIS_VERSION:
                self._export_qgis_version(self.CACHE_DETECTED_QGIS_VERSION)
            return

        if opersys not in ("linux", "win32"):
            logger.error(f"This job does not support your operating system: {opersys}")
            return

        installed_qgis_version_and_path = self.get_installed_qgis_version_and_path()

        if installed_qgis_version_and_path:
            version_str, installed_qgis_path = installed_qgis_version_and_path
            logger.debug(
                f"{self.ID}: {ENV_VAR_QGIS_EXE_PATH} is now {installed_qgis_path}"
            )
            os.environ[ENV_VAR_QGIS_EXE_PATH] = installed_qgis_path
            self._export_qgis_version(version_str)
        else:
            if self.options.get("if_not_found", "warning") == "error":
                raise QgisInstallNotFoundError()
            else:
                logger.warning(
                    "No QGIS installation found in "
                    f"{self._get_search_paths_with_environment_variable()}"
                )

        # log
        logger.debug(f"Job {self.ID} ran successfully.")

    def _export_qgis_version(self, version_str: str) -> None:
        """Export the detected QGIS version as an environment variable.

        Args:
            version_str (str): QGIS version, typically a SemVer string like `3.40.1`.
        """
        logger.debug(f"{self.ID}: {ENV_VAR_QGIS_VERSION} is now {version_str}")
        os.environ[ENV_VAR_QGIS_VERSION] = version_str

    # -- INTERNAL LOGIC ------------------------------------------------------
    def run_needed(self) -> bool:
        """Check if running the job is needed.

        Returns:
            bool: return True if job must be run, False otherwise
        """
        if qgis_bin_path := self.os_config.get_qgis_bin_path(use_fallback=False):
            if check_path_exists(input_path=qgis_bin_path, raise_error=False):
                logger.info(
                    f"{ENV_VAR_QGIS_EXE_PATH} defined and path {qgis_bin_path} "
                    f"exists so it gonna be used for QGIS executable. {self.ID} job "
                    "is skipped. "
                )
                version_str = self._get_qgis_bin_version(qgis_bin_path)
                if version_str:
                    logger.info(
                        f"{ENV_VAR_QGIS_EXE_PATH} defined and path {qgis_bin_path} "
                        f"exists for QGIS {version_str}. {self.ID} job is skipped. "
                    )
                    self.CACHE_DETECTED_QGIS_VERSION = version_str
                    return False
                else:
                    logger.warning(
                        f"The QGIS version can't be defined from the path {qgis_bin_path}. "
                        "If this behavior is not expected, check the environment variable."
                    )
                    return False
        logger.debug(
            f"'{ENV_VAR_QGIS_EXE_PATH}' is not defined. Searching for QGIS "
            "executable is necessary."
        )
        return True

    def get_installed_qgis_path(self) -> str | None:
        """Get the path to the installed QGIS executable best matching job options.

        Returns:
            str | None : installed qgis path
        """
        result = self.get_installed_qgis_version_and_path()
        return result[1] if result else None

    def get_installed_qgis_version_and_path(self) -> tuple[str, str] | None:
        """Get the installed QGIS version and executable path best matching job
        options.

        Returns:
            tuple[str, str] | None: (version, path) tuple, or None if no QGIS
                installation is found.
        """
        if opersys == "linux":
            found_versions = self._get_linux_installed_qgis_path()
        elif opersys == "win32":
            found_versions = self._get_windows_installed_qgis_path()

        if len(found_versions) == 0:
            return None

        logger.debug(f"Found installed QGIS: {found_versions}")
        latest_version = self._get_latest_version_from_list(
            versions=list(found_versions.keys())
        )

        # Define used version from version priority
        version_priority: list[str] = []
        if "version_priority" in self.options:
            version_priority = self.options["version_priority"]

        # Add preferred qgis version on top of the list
        if "QDT_PREFERRED_QGIS_VERSION" in environ:
            version_priority.insert(0, environ["QDT_PREFERRED_QGIS_VERSION"])

        # reverse lookup to retrieve the version string matching a given path
        path_to_version = {path: version for version, path in found_versions.items()}

        for version in version_priority:
            if latest_matching_path := self._get_latest_matching_version_path(
                found_versions=found_versions, version=version
            ):
                return path_to_version[latest_matching_path], latest_matching_path

        latest_qgis = found_versions[latest_version]
        if len(version_priority) != 0:
            # No version found in version priority
            version_priority_str = ",".join(self.options["version_priority"])
            logger.info(
                f"QGIS version(s) [{version_priority_str}] not found. Using most "
                f"recent found version {latest_version} : {latest_qgis}"
            )

        return latest_version, latest_qgis

    @staticmethod
    def _get_latest_version_from_list(versions: list[str]) -> str | None:
        """Get latest version from a list.

        Args:
            versions (list[str]): list of found version

        Returns:
            str | None: latest version, None if no version provided
        """
        if not versions:
            return None
        return max(versions, key=JobQgisInstallationFinder._version_sort_key)

    @staticmethod
    def _version_sort_key(version_str: str) -> Version:
        """Transforn a version string into a sortable and comparable Version object.

        Args:
            version_str (str): version string to parse, typically `X.Y.Z`.

        Returns:
            Version: parsed version, or `Version("0")` if parsing failed.
        """
        try:
            return Version(version_str)
        except InvalidVersion:
            logger.warning(
                f"Unparsable QGIS version, ignored for latest-version comparison: "
                f"{version_str}"
            )
            return Version("0")

    @staticmethod
    def _get_latest_matching_version_path(
        found_versions: dict[str, str], version: str
    ) -> str | None:
        """Get latest version path matching a wanted version.

        Args:
            found_versions (dict[str, str]): dict of found versions
            version (str): wanted version

        Returns:
            str | None: latest matching version path, None if not found
        """
        match_versions = []
        for found_version in found_versions.keys():
            if found_version.startswith(version):
                match_versions.append(found_version)
        # Use latest version
        if latest_version := JobQgisInstallationFinder._get_latest_version_from_list(
            match_versions
        ):
            return found_versions[latest_version]
        return None

    @staticmethod
    def _get_qgis_versions_in_dir(
        search_dir: str, search_patterns: list[str], found_version: dict[str, str]
    ) -> None:
        """Get QGIS binary path from an install directory.

        Args:
            install_dir (str): install directory
            search_patterns (list[str]): list of search pattern for qgis binary
            found_version (dict[str, str]): updated dict of qgis binary path and version
        """
        matchs = []

        logger.debug(
            f"Searching for QGIS binary in {search_dir} with pattern {search_patterns}"
        )

        for pattern in search_patterns:
            matchs += [file for file in Path(search_dir).rglob(pattern)]

        for match in matchs:
            if match.is_file():
                JobQgisInstallationFinder._search_qgis_version_and_add_to_dict(
                    qgis_bin=str(match), found_version=found_version
                )

    def _get_search_paths_with_environment_variable(self) -> list[str]:
        """Get search_paths option with environment variable update.

        Returns:
            list[str]: search_paths
        """
        # search_paths
        search_paths = []
        if "search_paths" in self.options:
            for path in self.options["search_paths"]:
                search_paths.append(expandvars(expanduser(getenv(path, path))))  # noqa: PTH111
        return search_paths

    def _get_windows_installed_qgis_path(self) -> dict[str, str]:
        """Get dict of installed QGIS version in common install directory.

        Returns:
            dict[str, str]: dict of QGIS version and QGIS bin path
        """

        # Get list of search path
        search_paths = self._get_search_paths_with_environment_variable()
        if len(search_paths) == 0:
            # Program files
            prog_file_dir = expandvars("%PROGRAMFILES%")

            for prog_files_subfolder in Path(prog_file_dir).iterdir():
                # Check if the directory name matches the pattern
                match = RE_QGIS_FINDER_DIR.match(prog_files_subfolder.name)
                if match:
                    search_paths.append(f"{prog_files_subfolder.resolve()}")

            # OSGEO4W
            search_paths.append(environ.get("QDT_OSGEO4W_INSTALL_DIR", "C:\\OSGeo4W"))

        return JobQgisInstallationFinder._get_qgis_found_version_dict_from_search_paths(
            search_paths=search_paths,
            search_patterns=["qgis-bin.exe", "qgis-ltr-bin.exe"],
        )

    @staticmethod
    def _get_qgis_found_version_dict_from_search_paths(
        search_paths: list[str], search_patterns: list[str]
    ) -> dict[str, str]:
        """Define qgis found version dict from a list of search path.

        If identical version are found in multiple path, the first version found in
        search_path is used.

        Args:
            search_paths (list[str]): list of search paths
            search_patterns (list[str]): list of search pattern for qgis binary

        Returns:
            dict[str, str]: dict of qgis binary path for qgis version
        """
        # We search reversed to have the version defined in priority with the first value
        found_version = {}
        for search_path in reversed(search_paths):
            JobQgisInstallationFinder._get_qgis_versions_in_dir(
                search_path, search_patterns, found_version
            )

        return found_version

    @staticmethod
    def _search_qgis_version_and_add_to_dict(
        qgis_bin: str, found_version: dict[str, str]
    ) -> None:
        """Search qgis version from qgis binary and add to found_version dict if found

        Args:
            qgis_bin (str): qgis binary path
            found_version (dict[str, str]): updated dict of qgis binary path and version
        """
        version_str = JobQgisInstallationFinder._get_qgis_bin_version(qgis_bin=qgis_bin)
        if version_str:
            logger.debug(f"QGIS version {version_str} found : {qgis_bin}")
            found_version[version_str] = qgis_bin
        else:
            logger.warning(f"Can't define QGIS version for '{qgis_bin}' file.")

    def _get_linux_installed_qgis_path(self) -> dict[str, str]:
        """Get install qgis path for linux operating system with which

        Returns:
            dict[str, str]: dict of QGIS version and QGIS bin path
        """

        # search_paths
        search_paths = self._get_search_paths_with_environment_variable()

        found_version = (
            JobQgisInstallationFinder._get_qgis_found_version_dict_from_search_paths(
                search_paths=search_paths, search_patterns=["qgis"]
            )
        )

        # use which to find installed qgis
        if qgis_bin := which("qgis"):
            logger.debug(f"QGIS path found using which: {qgis_bin}")
            JobQgisInstallationFinder._search_qgis_version_and_add_to_dict(
                qgis_bin=qgis_bin, found_version=found_version
            )

        return found_version

    @staticmethod
    def _get_qgis_bin_version(qgis_bin: str) -> str | None:
        """Get QGIS bin version with --version.

        See:

        - <https://runebook.dev/en/docs/python/library/subprocess/windows-popen-helpers>
        - <https://docs.python.org/fr/3.14/library/subprocess.html>

        Args:
            qgis_bin (str): QGIS bin executable path

        Returns:
            str | None: SemVer version, None if version not found
        """
        try:
            process = subprocess.run(  # noqa: S603  # nosec B603
                [qgis_bin, "--version"],
                capture_output=True,
                check=False,
                encoding="UTF-8",
                errors="replace",
                timeout=QGIS_VERSION_LOOKUP_TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            logger.warning(
                f"Getting QGIS version from '{qgis_bin}' timed out after "
                f"{QGIS_VERSION_LOOKUP_TIMEOUT_SECONDS}s. If you think that because your"
                " system is slow, you can adjust this delay using "
                "'QGIS_VERSION_LOOKUP_TIMEOUT_SECONDS' environment variable."
            )
            return None
        except (OSError, ValueError) as err:
            logger.error(f"Unable to run '{qgis_bin} --version'. Trace: {err}")
            return None

        if process.returncode != 0:
            logger.debug(
                f"'{qgis_bin} --version' exited with code {process.returncode}. "
                f"stderr: {process.stderr.strip()}"
            )

        version_match = RE_QGIS_FINDER_VERSION.match(process.stdout)
        if version_match:
            return version_match.group(1)
        return None
