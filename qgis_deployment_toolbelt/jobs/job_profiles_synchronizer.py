#! python3  # noqa: E265

"""
Synchronize profiles between downloaded (in QDT working folder) and installed
    profiles (in QGIS profiles'folder).

Author: Julien Moura (https://github.com/guts)
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from collections.abc import Iterable
from pathlib import Path
from shutil import copy2, copytree

# package
from qgis_deployment_toolbelt.jobs.generic_job import GenericJob
from qgis_deployment_toolbelt.profiles.qdt_profile import QdtProfile


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Classes ###############
# ##################################


class JobProfilesSynchronizer(GenericJob):
    """
    Job to synchronize profiles between downloaded (in QDT working folder) and installed
        profiles (in QGIS profiles'folder).
    """

    ID: str = "qprofiles-synchronizer"
    OPTIONS_SCHEMA: dict = {
        "sync_mode": {
            "type": str,
            "required": False,
            "default": "only_missing",
            "possible_values": (
                "only_missing",
                "only_different_version",
                "only_new_version",
                "overwrite",
            ),
            "condition": "in",
        },
    }
    PROFILES_NAMES_DOWNLOADED: list = []
    PROFILES_NAMES_INSTALLED: list = []

    def __init__(self, options: dict) -> None:
        """Instantiate the class.

        Args:
            options (List[dict]): list of dictionary with environment variables to set
            or remove.
        """
        super().__init__()
        self.options: dict = self.validate_options(options)

        # where QDT downloads remote repositories
        self.qdt_downloaded_repositories.mkdir(exist_ok=True, parents=True)
        logger.debug(f"Local repositories folder: {self.qdt_downloaded_repositories}")

    def run(self) -> None:
        """Execute job logic."""
        # check of there are some profiles folders within the downloaded folder
        li_qdt_profiles_from_folder = self.list_downloaded_profiles()
        if li_qdt_profiles_from_folder is None:
            logger.error("No QGIS profile found in the downloaded folder.")
            return

        # store downloaded profiles names
        self.PROFILES_NAMES_DOWNLOADED = [d.name for d in li_qdt_profiles_from_folder]
        logger.info(
            f"{len(self.PROFILES_NAMES_DOWNLOADED)} downloaded profiles: "
            f"{', '.join(self.PROFILES_NAMES_DOWNLOADED)}"
        )

        # copy profiles to the QGIS 3
        self.sync_installed_profiles_from_downloaded_profiles(
            downloaded_profiles=li_qdt_profiles_from_folder
        )

        logger.debug(f"Job {self.ID} ran successfully.")

    def compare_downloaded_with_installed_profiles(
        self, li_downloaded_profiles: Iterable[QdtProfile]
    ) -> tuple[list[QdtProfile], list[QdtProfile], list[QdtProfile]]:
        """Compare versions between downloaded (in QDT working folder) and installed
            (in QGIS) profiles.

        Args:
            li_downloaded_profiles (Iterable[QdtProfile]): downloaded profiles.

        Returns:
            tuple[list[QdtProfile], list[QdtProfile], list[QdtProfile]]: a tuple with
            the following structure (
                list of installed profiles which are outdated (lesser version number),
                list of installed profiles with a different version (lesser or greater),
                list of profiles with the same version number in downloaded/installed
                )
        """
        li_profiles_outdated = []
        li_profiles_different = []
        li_profiles_equal = []

        for downloaded_profile in li_downloaded_profiles:
            if (
                not downloaded_profile.version
                or not downloaded_profile.is_loaded_from_json
            ):
                logger.error(
                    "Unable to load profile.json from downloaded profile "
                    f"{downloaded_profile}, so it's impossible to compare "
                    "versions."
                )
                continue

            if Path(downloaded_profile.path_in_qgis, "profile.json").is_file():
                profile_installed: QdtProfile = QdtProfile.from_json(
                    profile_json_path=Path(
                        downloaded_profile.path_in_qgis, "profile.json"
                    ),
                    profile_folder=downloaded_profile.path_in_qgis,
                )
            else:
                logger.error(
                    "Unable to load profile.json from installed profile "
                    f"{downloaded_profile.path_in_qgis}, so it's impossible to compare "
                    "versions."
                )
                profile_installed: QdtProfile = QdtProfile(
                    folder=downloaded_profile.path_in_qgis, version="0.0.0"
                )

            # compare
            if profile_installed.is_older_than(downloaded_profile):
                li_profiles_outdated.append(downloaded_profile)
            elif profile_installed.version != downloaded_profile.version:
                li_profiles_different.append(downloaded_profile)
            elif profile_installed.version == downloaded_profile.version:
                li_profiles_equal.append(downloaded_profile)
            else:
                continue

        return li_profiles_outdated, li_profiles_different, li_profiles_equal

    def sync_installed_profiles_from_downloaded_profiles(
        self, downloaded_profiles: Iterable[QdtProfile]
    ) -> None:
        """Copy downloaded profiles to QGIS profiles folder. If the QGIS profiles folder
            doesn't exist, it will be created and every downloaded profile will be
            copied. If a profile is already installed, it won't be overwritten.

        Args:
            downloaded_profiles (tuple[QdtProfile]): list of downloaded profiles objects
        """
        logger.debug(f"Sync mode: {self.options.get('sync_mode')}.")
        # if local profiles folder exists or it's empty -> copy downloaded profiles
        if not self.qgis_profiles_path.exists() or not any(
            self.qgis_profiles_path.iterdir()
        ):
            logger.info(
                "The QGIS profiles folder does not exist or is empty: "
                f"{self.qgis_profiles_path.resolve()}. Probably a fresh install. "
                "Copying downloaded profiles..."
            )

            # copy all downloaded profiles
            self.sync_overwrite_local_profiles(profiles_to_copy=downloaded_profiles)

        elif self.options.get("sync_mode") == "only_missing":
            already_installed = []
            not_installed = []
            for dl_profile in downloaded_profiles:
                if not dl_profile.path_in_qgis.is_dir() or not any(
                    dl_profile.path_in_qgis.iterdir()
                ):
                    not_installed.append(dl_profile)
                else:
                    already_installed.append(dl_profile)

            if not len(not_installed):
                logger.info(
                    f"Each of the {len(downloaded_profiles)} downloaded plugins are "
                    "already installed."
                )
                compare_for_info = self.compare_downloaded_with_installed_profiles(
                    li_downloaded_profiles=downloaded_profiles
                )
                if len(compare_for_info[0]):
                    logger.info(
                        f"{compare_for_info[0]} of installed plugins are outdated comparing with"
                        f" downloaded ones: {','.join([p.name for p in compare_for_info[0]])}."
                    )
                elif len(compare_for_info[1]):
                    logger.info(
                        f"{compare_for_info[1]} of installed plugins are outdated comparing with"
                        f" downloaded ones: {','.join([p.name for p in compare_for_info[1]])}."
                    )
                else:
                    logger.info("Everything is up-to-date. Nothing to do!")
                return

            info_msg = (
                f"Mixed case. {len(not_installed)} are not installed: "
                f"{','.join([p.name for p in not_installed])}."
            )
            if len(already_installed):
                info_msg += (
                    f" {len(already_installed)} are already installed: "
                    f"{','.join([p.name for p in already_installed])}."
                )

            logger.info(info_msg)

            self.sync_overwrite_local_profiles(profiles_to_copy=not_installed)

        elif self.options.get("sync_mode") == "only_new_version":
            outdated = self.compare_downloaded_with_installed_profiles(
                li_downloaded_profiles=downloaded_profiles
            )[0]
            if not outdated:
                logger.info(
                    "All installed profiles are up-to-date with downloaded ones."
                )
                return
            self.sync_overwrite_local_profiles(profiles_to_copy=outdated)
        elif self.options.get("sync_mode") == "only_different_version":
            outdated, different, same = self.compare_downloaded_with_installed_profiles(
                li_downloaded_profiles=downloaded_profiles
            )
            if not different and not outdated:
                logger.info(
                    f"All installed profiles are the same as downloaded ones: {len(same)}"
                )
                return
            self.sync_overwrite_local_profiles(profiles_to_copy=different + outdated)
        elif self.options.get("sync_mode") == "overwrite":
            logger.debug(
                "Installed profiles are going to be overridden by downloaded ones."
            )
            # copy all downloaded profiles
            self.sync_overwrite_local_profiles(
                profiles_to_copy=downloaded_profiles, overwrite=True
            )

        else:
            logger.debug(
                "QGIS Profiles folder already exists, it's not empty: "
                f"{self.qgis_profiles_path.resolve()}"
            )

    def sync_overwrite_local_profiles(
        self, profiles_to_copy: tuple[QdtProfile], overwrite: bool = False
    ) -> None:
        """Overwrite local profiles with downloaded ones.

        Args:
            profiles_to_copy (tuple[QdtProfile]): tuple of profiles to copy
            overwrite (bool): overwrite profile if it exists (default False)
        """

        # copy downloaded profiles into this
        for d in profiles_to_copy:
            if overwrite:
                logger.info(f"Copying {d.folder} to {d.path_in_qgis}")
                d.path_in_qgis.mkdir(parents=True, exist_ok=True)
                copytree(
                    d.folder,
                    d.path_in_qgis,
                    copy_function=copy2,
                    dirs_exist_ok=True,
                )

            # Environment variable will be converted during merge
            logger.info(f"Merging {d.folder} to {d.path_in_qgis}")
            installed_profile = QdtProfile(folder=d.path_in_qgis)
            d.merge_to(installed_profile)
