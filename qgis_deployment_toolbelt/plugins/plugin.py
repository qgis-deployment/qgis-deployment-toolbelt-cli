#! python3  # noqa: E265

"""
Plugin object model.

Author: Julien Moura (https://github.com/guts)
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# special
from __future__ import annotations

# Standard library
import configparser
import logging
import zipfile
from dataclasses import dataclass, fields
from enum import Enum
from os.path import expanduser, expandvars
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

# 3rd party
from packaging.version import InvalidVersion, Version

# package
from qgis_deployment_toolbelt.utils.check_path import check_path
from qgis_deployment_toolbelt.utils.slugger import sluggy


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)

# #############################################################################
# ########## Classes ###############
# ##################################


class QgisPluginLocation(Enum):
    local = 1
    remote = 2


@dataclass
class QgisPlugin:
    """Model describing a QGIS plugin."""

    # optional mapping on attributes names.
    # Structure: {attribute_name_in_output_object: attribute_name_from_input_file}  # noqa: ERA001
    ATTR_MAP = {
        "location": "type",
        "qgis_maximum_version": "qgisMaximumVersion",
        "qgis_minimum_version": "qgisMinimumVersion",
    }

    OFFICIAL_REPOSITORY_URL_BASE = "https://plugins.qgis.org/"
    OFFICIAL_REPOSITORY_XML = "https://plugins.qgis.org/plugins/plugins.xml"

    name: str
    folder_name: str = None
    location: QgisPluginLocation = "remote"
    official_repository: bool = None
    plugin_id: int = None
    qgis_maximum_version: str = None
    qgis_minimum_version: str = None
    repository_url_xml: str = None
    url: str = None
    version: str = "latest"

    @classmethod
    def from_dict(cls, input_dict: dict) -> QgisPlugin:
        """Create object from a dictionary.

        Args:
            input_dict (dict): input dictionary

        Returns:
            QgisPlugin: instanciated object
        """
        # map attributes names
        for k, v in cls.ATTR_MAP.items():
            if v.lower() in input_dict.keys():
                input_dict[k] = input_dict.pop(v.lower(), None)

        # official repository autodetection
        if input_dict.get("repository_url_xml") == cls.OFFICIAL_REPOSITORY_XML:
            input_dict["official_repository"] = True
        elif (
            input_dict.get("url")
            and isinstance(input_dict.get("url"), str)
            and input_dict.get("url").startswith(cls.OFFICIAL_REPOSITORY_URL_BASE)
        ):
            input_dict["official_repository"] = True
            input_dict["repository_url_xml"] = cls.OFFICIAL_REPOSITORY_XML
        else:
            pass

        # URL auto build
        if input_dict.get("official_repository") is True and not input_dict.get("url"):
            input_dict["url"] = (
                f"{cls.OFFICIAL_REPOSITORY_URL_BASE}"
                f"plugins/{input_dict.get('folder_name') or input_dict.get('name')}/"
                f"version/{input_dict.get('version')}/download/"
            )
            input_dict["repository_url_xml"] = cls.OFFICIAL_REPOSITORY_XML
            input_dict["location"] = "remote"

        # remove keys which are not in object attributes
        attributes_names = [f.name for f in fields(cls)]
        for k in list(input_dict):
            if k not in attributes_names:
                del input_dict[k]

        # return new instance with loaded object
        return cls(
            **input_dict,
        )

    @classmethod
    def from_plugin_folder(cls, input_plugin_folder: Path) -> QgisPlugin:
        """Create object from a QGIS plugin folder. Must contain a metadata.txt file.

        Args:
            input_plugin_folder (Path): path to the folder containgin a QGIS plugin

        Returns:
            QgisPlugin: instanciated object
        """
        # check that input path is a folder
        check_path(
            input_path=input_plugin_folder,
            must_exists=True,
            must_be_a_folder=True,
            must_be_a_file=False,
            must_be_readable=True,
        )
        # check if the folder contains a metadata.txt file
        plugin_metadata_txt = input_plugin_folder / "metadata.txt"
        check_path(
            input_path=plugin_metadata_txt,
            must_be_a_file=True,
            must_be_readable=True,
            must_exists=True,
        )

        # read it
        with plugin_metadata_txt.open(encoding="UTF-8") as config_file:
            config = configparser.ConfigParser(strict=False)
            config.read_file(config_file)
        plugin_md_as_dict = {k: v for k, v in config.items(section="general")}

        # add folder name
        plugin_md_as_dict["folder_name"] = input_plugin_folder.name

        return cls.from_dict(plugin_md_as_dict)

    @classmethod
    def from_zip(cls, input_zip_path: Path) -> QgisPlugin:
        """Create object from a ZIP file.

        Args:
            input_zip_path (Path): filepath of the input zip

        Returns:
            QgisPlugin: instanciated object
        """
        with zipfile.ZipFile(file=input_zip_path) as zf:
            # find the metadata.txt file
            for i in zf.infolist():
                if not i.is_dir() and i.filename.split("/")[1] == "metadata.txt":
                    break

            # open and read it
            zip_path = zipfile.Path(zf)
            metadata_file = zip_path / i.filename
            plugin_folder_name = metadata_file.parent.name
            with metadata_file.open(encoding="UTF-8") as config_file:
                config = configparser.ConfigParser(strict=False)
                config.read_file(config_file)

        plugin_md_as_dict = {k: v for k, v in config.items(section="general")}

        # add folder name
        plugin_md_as_dict["folder_name"] = plugin_folder_name

        return cls.from_dict(plugin_md_as_dict)

    @property
    def download_url(self) -> str | None:
        """Try to guess download URL if it's not set during the object init.

        Returns:
            str: download URL
        """
        if self.url:
            return self.url
        elif self.repository_url_xml and self.folder_name and self.version:
            split_url = urlsplit(self.repository_url_xml)
            new_url = split_url._replace(path=split_url.path.replace("plugins.xml", ""))
            return f"{urlunsplit(new_url)}{self.folder_name}.{self.version}.zip"
        elif self.repository_url_xml and self.name and self.version:
            split_url = urlsplit(self.repository_url_xml)
            new_url = split_url._replace(path=split_url.path.replace("plugins.xml", ""))
            return f"{urlunsplit(new_url)}{self.name}.{self.version}.zip"
        else:
            return None

    @property
    def id_with_version(self) -> str:
        """Unique identifier using plugin_id (if set) and name + version slugified.

        Returns:
            str: plugin identifier meant to be unique per version
        """
        if self.plugin_id:
            return f"{self.plugin_id}_{sluggy(self.name)}_{sluggy(self.version.replace('.', '-'))}"
        else:
            return f"{sluggy(self.name)}_{sluggy(self.version.replace('.', '-'))}"

    @property
    def installation_folder_name(self) -> str:
        """Name of the folder when the plugin is installed into QGIS/profile/python/plugins/. \
            If not clearly specified intot the profile.json, it tries to extract it from \
            the download URL. As final fallback, it returns the slufigied plugin name.

        Returns:
            str: plugin folder name
        """
        if self.folder_name:
            return self.folder_name
        elif self.download_url:
            try:
                folder_name_from_url = urlsplit(self.download_url).path.split("/")[2]
                self.folder_name = folder_name_from_url
                return folder_name_from_url
            except Exception as err:
                logger.error(
                    f"Plugin {self.name} - Determine plugin folder name from download"
                    f"URL failed. Please specify it into profile.json file. Trace: {err}"
                )
                return sluggy(self.name)
        else:
            return sluggy(self.name)

    def is_older_than(self, version_to_compare: str | QgisPlugin) -> bool | None:
        """Determine if the actual object version is older than the given version to \
            compare.

        Args:
            version_to_compare (Union[str, QgisPlugin]): given version to compare with object version

        Returns:
            bool: True if the given version is newer (more recent)
        """
        if not any([self.version, version_to_compare]):
            logger.error("Object version is not set, so the comparizon is impossible.")
            return None

        # if a plugin is given
        if isinstance(version_to_compare, QgisPlugin):
            # take the opportunity to check the name is the same
            if not self.name == version_to_compare.name:
                logger.warning(
                    "Be careful, the plugin to compare seems to be different: "
                    f"{self.name} != {version_to_compare.name}"
                )
            # store the version string
            version_to_compare = version_to_compare.version

        # load object version as packaging.Version object
        try:
            plugin_version = Version(self.version)
        except InvalidVersion as err:
            logger.error(
                f"Plugin {self.name} (current) uses an incompatible versioning scheme: "
                f"{self.version}. It's not Semver (even prefixed by 'v'), nor Calver or "
                "any of supported specification. See https://peps.python.org/pep-0440/. "
                f"Trace: {err}"
            )
            return None

        # load version to compare as packaging.Version object
        try:
            version_to_compare = Version(version_to_compare)
        except InvalidVersion as err:
            logger.error(
                f"Plugin {self.name} (to compare) uses an incompatible versioning scheme: "
                f"{self.version}. It's not Semver (even prefixed by 'v'), nor Calver or "
                "any of supported specification. See https://peps.python.org/pep-0440/. "
                f"Trace: {err}"
            )
            return None

        logger.debug(f"Comparing versions: {plugin_version} and {version_to_compare}")

        return plugin_version < version_to_compare

    @property
    def uri_to_zip(self) -> str | Path:
        """Get the plugin URI. Can be either a local path or remote URL (in that case
            it's mapped to dowload_url property).

        Returns:
            str: URI (path or URL) to the plugin ZIP archive
        """
        if (
            self.url
            and isinstance(self.url, str)
            and self.url.startswith(("http://", "https://"))
        ):
            return self.download_url
        elif (
            self.url
            and isinstance(self.url, str)
            and (self.url.startswith("file://") or Path(self.url))
        ):
            uri_or_path = self.url
            if self.url.startswith("file://"):
                uri_or_path = self.url[7:]
                logger.debug(
                    f"URI cleaning: 'file://' protocol prefix removed. Result: {uri_or_path}"
                )
            return Path(expandvars(expanduser(uri_or_path)))  # noqa: PTH111
        else:
            return self.url
