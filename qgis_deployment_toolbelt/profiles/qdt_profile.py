#! python3  # noqa: E265

"""
QDT QGIS Profile object and related sugar.

Author: Julien Moura (https://github.com/guts)
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# special
from __future__ import annotations

# standard
import json
import logging
import tempfile
from pathlib import Path
from shutil import copy2, copytree
from typing import Any, Literal, cast, get_args

# 3rd party
from packaging.version import InvalidVersion, Version

# Package
from qgis_deployment_toolbelt.__about__ import __version_clean__
from qgis_deployment_toolbelt.constants import (
    COPY_IGNORED_PATTERNS,
    QGIS_PROFILE_CUSTOMIZATION_INI_FILENAME,
    RE_QGIS_PROFILE_INI_STEM,
    RE_QGIS_VERSIONED_FOLDER,
    OSConfiguration,
    SupportedQgisMajorVersion,
    get_qdt_working_directory,
)
from qgis_deployment_toolbelt.plugins.plugin import QgisPlugin
from qgis_deployment_toolbelt.profiles.qgis_ini_handler import QgisIniHelper
from qgis_deployment_toolbelt.utils.check_path import check_path


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Classes ###############
# ##################################
class QdtProfile:
    """Object definition for QGIS Profile handled by QDT."""

    # optional mapping on attributes names.
    # {attribute_name_in_output_object: attribute_name_from_input_file}  # noqa: ERA001
    ATTR_MAP = {
        "qdt_min_version": "qdtMinVersion",
        "qgis_maximum_version": "qgisMaximumVersion",
        "qgis_minimum_version": "qgisMinimumVersion",
    }

    def __init__(  # noqa: C901
        self,
        alias: str | None = None,
        author: str | None = None,
        description: str | None = None,
        email: str | None = None,
        folder: Path | None = None,
        icon: str | None = None,
        json_ref_path: Path | None = None,
        loaded_from_json: bool = False,
        name: str | None = None,
        plugins: list | None = None,
        qdt_min_version: str | None = None,
        qgis_maximum_version: str | None = None,
        qgis_minimum_version: str | None = None,
        rules: list[dict] | None = None,
        splash: str | None = None,
        version: str | None = None,
        **kwargs: Any,
    ):
        """Initialize a QDT Profile object.

        :param str name: name of the shortcut that will be created
        :param str author: profile author name
        """
        # store QDT working folder
        self.qdt_working_folder = get_qdt_working_directory()
        # retrieve operating system specific configuration
        self.os_config = OSConfiguration.from_opersys()

        # default values for immutable attributes
        self.loaded_from_json = loaded_from_json

        # default values for attributes/properties that can be get/set
        self._alias = None
        self._author = None
        self._description = None
        self._email = None
        self._folder = None
        self._icon = None
        self._json_ref_path = None
        self._name = None
        self._splash = None
        self._plugins = None
        self._qdt_min_version = None
        self._qgis_maximum_version = None
        self._qgis_minimum_version = None
        self._rules = None
        self._version = None

        # if values have been passed, so use them as objects attributes.
        # attributes are prefixed by an underscore '_'
        if alias:
            self._alias = alias
        if author:
            self._author = author
        if description:
            self._description = description
        if email:
            self._email = email
        if folder:
            self._folder = folder
        if icon:
            self._icon = icon
        if json_ref_path:
            self._json_ref_path = json_ref_path
        if name:
            self._name = name
        if plugins:
            self._plugins = plugins
        if qdt_min_version:
            self._qdt_min_version = qdt_min_version
        if qgis_maximum_version:
            self._qgis_maximum_version = qgis_maximum_version
        if qgis_minimum_version:
            self._qgis_minimum_version = qgis_minimum_version
        if rules:
            self._rules = rules
        if splash:
            self._splash = splash
        if version:
            self._version = version

    @classmethod
    def from_json(
        cls, profile_json_path: Path, profile_folder: Path | None = None
    ) -> QdtProfile:
        """Load profile from a profile.json file.

        Args:
            profile_json_path (Path): path to the profile json file
            profile_folder (Path | None, optional): path to the profile folder,
                defaults to None.

        Returns:
            QdtProfile: QdtProfile object with attributes filled from JSON.

        Example:

            .. code-block:: python

                QdtProfile = QdtProfile.from_json(Path(src_profile / "profile.json"))
                print(profile.splash.resolve())
        """
        # checks
        check_path(
            input_path=profile_json_path,
            must_be_a_file=True,
            must_exists=True,
            must_be_readable=True,
        )
        if profile_folder:
            check_path(
                input_path=profile_folder,
                must_be_a_folder=True,
                must_exists=True,
                must_be_readable=True,
            )

        # load JSON
        with profile_json_path.open(mode="r", encoding="utf8") as in_profile_json:
            profile_data = json.load(in_profile_json)

        # map attributes names
        for k, v in cls.ATTR_MAP.items():
            profile_data[k] = profile_data.pop(v, None)

        # return new instance with loaded object
        return cls(
            folder=profile_folder,
            json_ref_path=profile_json_path,
            loaded_from_json=True,
            **profile_data,
        )

    @property
    def alias(self) -> str:
        """Returns the profile's alias.

        :return str: profile alias
        """
        return self._alias

    @property
    def folder(self) -> Path | None:
        """Returns the path to the folder where the profile is stored.

        Returns:
            Path: profile folder path
        """
        if isinstance(self._folder, Path):
            return self._folder.resolve()
        else:
            return self._folder

    @property
    def is_loaded_from_json(self) -> bool:
        """Tells if the profile has been loaded from a JSON file.

        :return bool: True if the profile has been loaded from a JSON file
        """
        return self.loaded_from_json

    @property
    def icon(self) -> str | None:
        """Returns the icon as specified into the original profile.json.

        :return str: profile icon value
        """
        if self._icon:
            return self._icon

    @property
    def icon_path(self) -> Path:
        """Returns the path to the profile's icon into the profile folder.

        :return Path: profile icon path
        """
        if self._folder and self._icon:
            return self._folder.joinpath(self._icon)

    @property
    def json_ref_path(self) -> Path:
        """Returns the path to the corresponding JSON path.

        :return Path: profile json_ref_path path
        """
        return self._json_ref_path.resolve()

    @property
    def name(self) -> str | None:
        """Returns the profile's name. If not set, the folder name is used.

        Returns:
            str: profile's name
        """
        if self._name:
            return self._name
        elif self._folder:
            return self._folder
        else:
            return None

    @property
    def path_in_qgis(self) -> Path:
        """Returns the path to the folder where the profile is stored in QGIS
            (= installed).

        Returns:
            Path: path to the installed (i.e. in QGIS) profile folder
        """
        return self.os_config.qgis_profiles_path.joinpath(self.name)

    @property
    def plugins(self) -> list[QgisPlugin]:
        """Returns the plugins associated with the profile.

        Returns:
            List[QgisPlugin]: list of plugins
        """
        if self._plugins:
            return [QgisPlugin.from_dict(p) for p in self._plugins]
        else:
            return []

    @property
    def qgis_maximum_version(self) -> str | None:
        """Maximum QGIS version the profile is compatible with.

        Read from the `qgisMaximumVersion` key of the profile.json file.

        Returns:
            str | None: maximum QGIS version as string, None if the profile does not
                declare any upper bound.
        """
        return self._qgis_maximum_version

    @property
    def qgis_minimum_version(self) -> str | None:
        """Minimum QGIS version the profile is compatible with.

        Read from the `qgisMinimumVersion` key of the profile.json file.

        Returns:
            str | None: minimum QGIS version as string, None if the profile does not
                declare any lower bound.
        """
        return self._qgis_minimum_version

    @property
    def qgis_version_major(self) -> SupportedQgisMajorVersion | None:
        """QGIS major version deduced from the profile folder's parent directories.

        Works only for installed profiles and for folder structure following the
        official QGIS one ('QGIS/QGISX/profiles'), in case of custom profiles folder path.

        Returns:
            SupportedQgisMajorVersion | None: QGIS major version supported by QDT if it
                can be deduced from the profile path, None otherwise.
        """
        if not isinstance(self.folder, Path):
            logger.debug(
                f"Profile '{self._name}' has no folder set, so its QGIS major version "
                "can't be deduced from the path."
            )
            return None

        for parent_folder in self.folder.parents:
            version_match = RE_QGIS_VERSIONED_FOLDER.match(parent_folder.name)
            if version_match is None:
                continue

            qgis_version_major = int(version_match.group(1))
            if qgis_version_major not in get_args(SupportedQgisMajorVersion):
                logger.warning(
                    f"Profile '{self.name}' is stored under '{parent_folder}' which "
                    f"refers to QGIS {qgis_version_major}, not supported by QDT. "
                    "Supported major versions: "
                    f"{', '.join(map(str, get_args(SupportedQgisMajorVersion)))}. "
                    "Ignoring it."
                )
                return None

            logger.debug(
                f"QGIS major version {qgis_version_major} deduced for profile "
                f"'{self.name}' from its parent folder: {parent_folder}"
            )
            return cast("SupportedQgisMajorVersion", qgis_version_major)

        logger.debug(
            f"No QGIS versioned folder (QGIS3, QGIS4...) found in the parents of "
            f"'{self.folder}', so the QGIS major version of the profile "
            f"'{self.name}' can't be deduced from the path."
        )
        return None

    @property
    def rules(self) -> list[dict] | None:
        """Returns the rules associated with the profile.

        Returns:
            list[rules]: list of rules
        """
        return self._rules

    @property
    def splash(self) -> str | Path | None:
        """Returns the profile splash image as path if can be resolved or as string.

        Returns:
            Union[str, Path]: path to the profile splash image
        """
        if (
            self._splash
            and isinstance(self.folder, Path)
            and self.folder.joinpath(self._splash).is_file()
        ):
            return self.folder.joinpath(self._splash)
        else:
            return self._splash

    @property
    def qdt_min_version(self) -> str | None:
        """Returns the minimum QDT version required to deploy this profile.

        Returns:
            str | None: minimum QDT version or None if not set.
        """
        return self._qdt_min_version

    @property
    def version(self) -> str | None:
        """Returns the profile version as string.

        Returns:
            str: version
        """
        return self._version

    def is_qdt_version_compatible(self) -> tuple[bool | None, str | None]:
        """Check if the running QDT version satisfies this profile's
        `qdtMinVersion` attribute (if set).

        Returns:
            tuple[bool | None, str | None]: a tuple with a boolean (True if the
                running QDT version is compatible, False if it's too old, None if
                the comparison could not be performed) and an explicit message
                (None if compatible).
        """
        if not self.qdt_min_version:
            return True, None

        try:
            required_version = Version(str(self.qdt_min_version))
        except InvalidVersion as err:
            return (
                None,
                f"Profile '{self.name}' attribute 'qdtMinVersion' is not a valid "
                f"version: {self.qdt_min_version}. Trace: {err}",
            )

        try:
            running_version = Version(__version_clean__)
        except InvalidVersion as err:
            logger.warning(
                f"Unable to parse running QDT version ({__version_clean__}) to "
                f"check compatibility with profile '{self.name}' qdtMinVersion. "
                f"Trace: {err}"
            )
            return True, None

        if running_version < required_version:
            return (
                False,
                f"Profile '{self.name}' requires QGIS Deployment Toolbelt "
                f">= {required_version}, but the running version is "
                f"{running_version}. Please upgrade QDT.",
            )

        return True, None

    def is_older_than(self, version_to_compare: str | QdtProfile) -> bool | None:
        """Determine if the actual object version is older than the given version to
            compare.

        Args:
            version_to_compare (Union[str, QdtProfile]): given version to compare with object
            version

        Returns:
            bool: True if the given version is newer (more recent)
        """
        if not any([self.version, version_to_compare]):
            logger.error("Object version is not set, so the comparizon is impossible.")
            return None

        # if a profile is given
        if isinstance(version_to_compare, QdtProfile):
            # take the opportunity to check the name is the same
            if not self.name == version_to_compare.name:
                logger.warning(
                    "Be careful, the profile to compare seems to be different: "
                    f"{self.name} != {version_to_compare.name}"
                )
            # store the version string
            version_to_compare = version_to_compare.version

        # load object version as packaging.Version object
        try:
            profile_version = Version(self.version)
        except InvalidVersion as err:
            logger.error(
                f"Profile {self.name} uses an incompatible versioning scheme: {self.version}."
                "It's not Semver (even prefixed by 'v'), nor Calver or any of "
                "supported specification. See https://peps.python.org/pep-0440/. "
                f"Trace: {err}"
            )
            return None

        # load version to compare as packaging.Version object
        try:
            version_to_compare = Version(version_to_compare)
        except InvalidVersion as err:
            logger.error(
                f"Version to compare uses an incompatible versioning scheme: {self.version}."
                "It's not Semver (even prefixed by 'v'), nor Calver or any of "
                "supported specification. See https://peps.python.org/pep-0440/. "
                f"Trace: {err}"
            )
            return None

        logger.debug(f"Comparing versions: {profile_version} and {version_to_compare}")

        return profile_version < version_to_compare

    def status(self) -> Literal["downloaded", "installed", "unknown"]:
        """Determine current profile status: downloaded (in QDT working folder),
        installed (in the QGIS profiles folder) or unknown.

        Returns:
            str: one of "downloaded", "installed", "unknown"
        """
        if not isinstance(self.folder, Path):
            return "unknown"

        if self.folder.is_relative_to(self.os_config.qgis_profiles_path):
            return "installed"
        elif self.folder.is_relative_to(self.qdt_working_folder):
            return "downloaded"
        else:
            return "unknown"

    @property
    def installed_profile(self) -> QdtProfile | None:
        """Returns the installed profile object only if the corresponding profiles.json
            exists.

        Returns:
            QdtProfile | None: QdtProfile object if profile.json exists, else None
        """

        if self.status() == "installed":
            return self
        elif self.status() == "downloaded":
            if self.path_in_qgis.joinpath("profile.json").is_file():
                return self.from_json(
                    profile_json_path=self.path_in_qgis.joinpath("profile.json"),
                    profile_folder=self.path_in_qgis.resolve(),
                )
            else:
                # TODO: develop a class method to load a profile from a folder
                pass
        return None

    # -- QGIS*.ini files --
    @property
    def qgis_ini_filename(self) -> str:
        """Name of the QGIS settings file expected by the targeted QGIS installation.

        QGIS names it after its own major version: `QGIS3.ini` for QGIS 3, `QGIS4.ini`
        for QGIS 4.

        Returns:
            str: name of the profile settings ini file.
        """
        return self.os_config.qgis_profile_ini_filename

    @property
    def qgis_ini_filepath(self) -> Path:
        """Path to the QGIS settings file to work with in the profile folder.

        Returns:
            Path: path to the profile's QGIS settings file, which may not exist yet.
        """
        expected_ini_filepath = self.folder.joinpath("QGIS", self.qgis_ini_filename)
        if expected_ini_filepath.is_file():
            return expected_ini_filepath

        for candidate in sorted(self.folder.joinpath("QGIS").glob("QGIS*.ini")):
            if RE_QGIS_PROFILE_INI_STEM.match(candidate.stem):
                logger.info(
                    f"Profile '{self.name}' ships a '{candidate.name}' settings file "
                    f"but the targeted QGIS expects '{self.qgis_ini_filename}'. "
                    "The shipped file is used and will be renamed when installed."
                )
                return candidate

        return expected_ini_filepath

    def has_qgis_ini_file(self) -> bool:
        """Determine if a QGIS settings file (QGIS3.ini, QGIS4.ini...) exists in the
            profile folder.

        Returns:
            bool: True if a QGIS/QGIS*.ini file exists in the profile folder.
        """
        return check_path(
            input_path=self.qgis_ini_filepath,
            must_be_a_file=True,
            must_be_a_folder=False,
            must_be_readable=True,
            must_exists=True,
            raise_error=False,
        )

    def has_qgis_customization_ini_file(self) -> bool:
        """Determine if a QGIS/QGISCUSTOMIZATION3.ini file exists in the profile folder.

        Returns:
            bool: True if a QGIS/QGISCUSTOMIZATION3.ini file exists in the profile folder.
        """
        return check_path(
            input_path=self.folder.joinpath(
                "QGIS", QGIS_PROFILE_CUSTOMIZATION_INI_FILENAME
            ),
            must_be_a_file=True,
            must_be_a_folder=False,
            must_be_readable=True,
            must_exists=True,
            raise_error=False,
        )

    def get_qgis_ini_helper(self) -> QgisIniHelper:
        """Return the ini helper for the profile configuration.

        Returns:
            QgisIniHelper: Ini helper loaded with profile's QGIS/QGIS*.ini
        """
        ini_filepath = self.qgis_ini_filepath
        logger.debug(
            f"Returning {ini_filepath.name} helper for profile '{self.name}' using "
            f"this file: {ini_filepath}"
        )
        return QgisIniHelper(
            ini_filepath=ini_filepath,
            ini_type="profile_settings",
        )

    def get_qgis_customization_ini_helper(self) -> QgisIniHelper:
        """Return the ini helper for the profile customization.

        Returns:
            QgisIniHelper: Ini helper loaded with profile's QGIS/QGISCUSTOMIZATION3.ini
        """
        customization_ini_filepath = self.folder.joinpath(
            "QGIS", QGIS_PROFILE_CUSTOMIZATION_INI_FILENAME
        )
        logger.debug(
            f"Returning {QGIS_PROFILE_CUSTOMIZATION_INI_FILENAME} helper for profile "
            f"'{self.name}' using this file: {customization_ini_filepath}"
        )
        return QgisIniHelper(
            ini_filepath=customization_ini_filepath,
            ini_type="profile_customization",
            qgis_version_major=self.os_config.qgis_version_major,
        )

    def rename_qgis_ini_file_to_target_version(self) -> Path | None:
        """Rename the profile's QGIS settings file to match the targeted QGIS major
            version.

        A profile authored for QGIS 3 ships a `QGIS/QGIS3.ini` file, which QGIS 4
        silently ignores since it reads `QGIS/QGIS4.ini`. Renaming it keeps the
        settings shipped by the profile effective after an upgrade.

        Returns:
            Path | None: path to the renamed file, None if nothing has been renamed.
        """
        current_ini_filepath = self.qgis_ini_filepath
        if current_ini_filepath.name == self.qgis_ini_filename:
            return None

        if not current_ini_filepath.is_file():
            return None

        target_ini_filepath = current_ini_filepath.with_name(self.qgis_ini_filename)
        if target_ini_filepath.exists():
            logger.debug(
                f"Profile '{self.name}' ships both {current_ini_filepath.name} and "
                f"{target_ini_filepath.name}. Keeping them as they are."
            )
            return None

        current_ini_filepath.replace(target_ini_filepath)
        logger.info(
            f"Profile '{self.name}': {current_ini_filepath.name} renamed into "
            f"{target_ini_filepath.name} to comply with the targeted QGIS "
            f"{self.os_config.qgis_version_major}."
        )
        return target_ini_filepath

    def merge_to(self, dst: QdtProfile) -> None:
        """Merge QdtProfile to another profile.

        Args:
            dst (QdtProfile): profile to merge to (i.e. destination profile, typically the installed one)
        """
        with tempfile.TemporaryDirectory(
            prefix=f"QDT_merge_profile_{self.name}_", ignore_cleanup_errors=True
        ) as tmpdirname:
            logger.info(
                f"Merge profile {self.name} with {tmpdirname} temporary directory"
            )
            # Copy source QdtProfile folder
            copytree(
                self.folder,
                tmpdirname,
                copy_function=copy2,
                dirs_exist_ok=True,
                ignore=COPY_IGNORED_PATTERNS,
            )
            # Merge INI files
            tmp_profile = QdtProfile(folder=Path(tmpdirname))
            tmp_profile.os_config = self.os_config
            tmp_profile.rename_qgis_ini_file_to_target_version()

            # profile settings file: QGIS3.ini, QGIS4.ini...
            if self.has_qgis_ini_file() and dst.has_qgis_ini_file():
                # Copy current installed file
                copy2(
                    dst.get_qgis_ini_helper().ini_filepath,
                    tmp_profile.get_qgis_ini_helper().ini_filepath,
                )
                # Merge
                self.get_qgis_ini_helper().merge_to(tmp_profile.get_qgis_ini_helper())

            # profile customization file
            if (
                self.has_qgis_customization_ini_file()
                and dst.has_qgis_customization_ini_file()
            ):
                # Copy current installed file
                copy2(
                    dst.get_qgis_customization_ini_helper().ini_filepath,
                    tmp_profile.get_qgis_customization_ini_helper().ini_filepath,
                )
                # Merge
                self.get_qgis_customization_ini_helper().merge_to(
                    tmp_profile.get_qgis_customization_ini_helper()
                )

            logger.info(f"Copying {tmpdirname} to {dst.path_in_qgis}")
            copytree(
                tmpdirname,
                dst.path_in_qgis,
                copy_function=copy2,
                dirs_exist_ok=True,
                ignore=COPY_IGNORED_PATTERNS,
            )


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    """Standalone execution."""
    pass
