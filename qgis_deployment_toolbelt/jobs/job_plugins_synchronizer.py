#! python3  # noqa: E265

"""
Synchronize plugins between downloaded and installed profiles.

Author: Julien Moura (https://github.com/guts)
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from pathlib import Path
from shutil import ReadError, unpack_archive

# package
from qgis_deployment_toolbelt.jobs.generic_job import GenericJob
from qgis_deployment_toolbelt.plugins.plugin import QgisPlugin
from qgis_deployment_toolbelt.profiles.qdt_profile import QdtProfile


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Classes ###############
# ##################################


class JobPluginsSynchronizer(GenericJob):
    """
    Job to download and synchronize plugins.
    """

    ID: str = "qplugins-synchronizer"
    OPTIONS_SCHEMA: dict = {
        "action": {
            "type": str,
            "required": False,
            "default": "create_or_restore",
            "possible_values": ("create", "create_or_restore", "remove"),
            "condition": "in",
        },
        "profile_ref": {
            "type": str,
            "required": False,
            "default": "installed",
            "possible_values": ("downloaded", "installed"),
            "condition": None,
        },
        "source": {
            "type": str,
            "required": False,
            "default": None,
            "possible_values": None,
            "condition": None,
        },
    }

    def __init__(self, options: dict) -> None:
        """Instantiate the class.

        :param dict options:  job options.
        """
        super().__init__()
        self.options: dict = self.validate_options(options)

        # where QDT downloads plugins
        self.qdt_plugins_folder.mkdir(exist_ok=True, parents=True)
        logger.info(f"QDT plugins folder: {self.qdt_plugins_folder}")

        # which profile.json file to use
        if self.options.get("profile_ref") == "installed":
            self.profiles_path = self.qgis_profiles_path
            logger.debug(
                "Using plugins listed into profile.json files found into profiles "
                "already installed under the QGIS3 user folder: "
                f"{self.profiles_path.resolve()}"
            )
        else:
            self.profiles_path = self.qdt_working_folder
            logger.debug(
                "Using plugins listed into profile.json files found into profiles "
                f"downloaded under the QDT local folder: {self.profiles_path.resolve()}"
            )

    def run(self) -> None:
        """Execute job logic."""
        # local vars
        profile_plugins_to_create: list[tuple[QdtProfile, QgisPlugin, Path]] = []
        profile_plugins_to_restore = []
        profile_plugins_to_upgrade = []

        # get profiles, downloaded or installed
        qdt_profiles = self.filter_profiles_folder(
            start_parent_folder=self.profiles_path
        )

        if qdt_profiles is None:
            logger.error(
                f"No QGIS profile found in {self.options.get('profile_ref')} folder: "
                f"{self.profiles_path}"
            )
            return

        for qdt_profile in qdt_profiles:
            # determine folder
            if self.options.get("installed"):
                profile_plugins_folder = qdt_profile.folder / "python/plugins"
            else:
                profile_plugins_folder = qdt_profile.path_in_qgis / "python/plugins"

            # parse plugins in profile
            for expected_plugin in qdt_profile.plugins:
                # expected_plugin = expected version to be installed into the profile

                # is the plugin downloaded
                plugin_downloaded_zip_source = (
                    self.qdt_plugins_folder / f"{expected_plugin.id_with_version}.zip"
                )
                if not plugin_downloaded_zip_source.is_file():
                    logger.warning(
                        f"Profile {qdt_profile.name} - "
                        f"Plugin {expected_plugin.name} version "
                        f"{expected_plugin.version} should be installed but its "
                        f"archive is not found: {plugin_downloaded_zip_source}"
                    )
                    continue

                # check if the plugin is already installed or not
                plugin_installed_folder = Path(
                    profile_plugins_folder, expected_plugin.installation_folder_name
                )
                if not plugin_installed_folder.is_dir():
                    logger.debug(
                        f"Profile {qdt_profile.name} - "
                        f"Plugin {expected_plugin.name} is not present. It will be added."
                    )
                    profile_plugins_to_create.append(
                        (
                            qdt_profile,
                            expected_plugin,
                            plugin_downloaded_zip_source,
                        )
                    )
                    continue

                # if the plugin is already present into the profile
                plugin_installed: QgisPlugin = QgisPlugin.from_plugin_folder(
                    input_plugin_folder=plugin_installed_folder
                )

                # if the installed plugin has the same version, don't touch anything
                if plugin_installed.version == expected_plugin.version:
                    logger.debug(
                        f"Profile {qdt_profile.name} - "
                        f"Plugin {expected_plugin.name} is already installed "
                        f"with the expected version: {expected_plugin.version}"
                    )
                    continue

                # if versions are different
                if plugin_installed.is_older_than(expected_plugin):
                    logger.info(
                        f"Profile {qdt_profile.name} - "
                        f"Plugin {expected_plugin.name} is already installed "
                        f"but in an older version: {plugin_installed.version} < "
                        f"{expected_plugin.version}. It will be upgraded."
                    )
                    profile_plugins_to_upgrade.append(
                        (qdt_profile, expected_plugin, plugin_downloaded_zip_source)
                    )
                else:
                    logger.debug(
                        f"Profile {qdt_profile.name} - "
                        f"Plugin {expected_plugin.name} is already installed "
                        f"but in a newer version: {plugin_installed.version} > "
                        f"{expected_plugin.version}. It will be kept as is."
                    )

        # log parse results
        if not any(
            (
                profile_plugins_to_create,
                profile_plugins_to_restore,
                profile_plugins_to_upgrade,
            )
        ):
            logger.info(
                f"Every plugins are up to date in the {len(qdt_profiles)} profiles parsed."
            )
        else:
            self.install_plugin_into_profile(profile_plugins_to_create)
            self.install_plugin_into_profile(profile_plugins_to_upgrade)

        logger.debug(f"Job {self.ID} ran successfully.")

    # -- INTERNAL LOGIC ------------------------------------------------------
    def install_plugin_into_profile(
        self, list_plugins_to_profiles: list[tuple[QdtProfile, QgisPlugin, Path]]
    ):
        """Unzip downloaded plugins into the matching profiles.

        Args:
            list_plugins_to_profiles (List[Tuple[QdtProfile, QgisPlugin, Path]]): list \
                of tuples containing the target profile, the plugin object and the ZIP path.
        """
        for profile, plugin, source_path in list_plugins_to_profiles:
            if self.options.get("installed"):
                profile_plugins_folder = profile.folder / "python/plugins"
            else:
                profile_plugins_folder = profile.path_in_qgis / "python/plugins"

            # make sure destination folder exists
            profile_plugins_folder.mkdir(parents=True, exist_ok=True)

            # in some cases related to proxies issues, the plugin archive download
            # returns a success but in fact it's just some HTML error from the proxy
            # (but with wrong HTTP error code...) so the ZIP file is not really a zip...
            try:
                unpack_archive(filename=source_path, extract_dir=profile_plugins_folder)
            except ReadError as err:
                logger.error(
                    f"Plugin {plugin.name} ({plugin.version}) could not be unzipped nor "
                    f"installed in profile {profile.name}. Probably because of corrupted "
                    f"zip file. Is the plugin download worked before? Trace: {err}"
                )
                continue

            logger.info(
                f"Profile {profile.name} - "
                f"Plugin {plugin.name} {plugin.version} has been unzipped from "
                f"{source_path} to {profile_plugins_folder}"
            )


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    """Standalone execution."""
    pass
