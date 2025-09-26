#! python3  # noqa: E265

"""
Download plugins listed into profiles.

Author: Julien Moura (https://github.com/guts)
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from concurrent.futures import ThreadPoolExecutor
from os import getenv
from pathlib import Path
from shutil import copy2

# package
from qgis_deployment_toolbelt.__about__ import __title_clean__
from qgis_deployment_toolbelt.jobs.generic_job import GenericJob
from qgis_deployment_toolbelt.plugins.plugin import QgisPlugin
from qgis_deployment_toolbelt.utils.check_path import check_path
from qgis_deployment_toolbelt.utils.file_downloader import download_remote_file_to_local
from qgis_deployment_toolbelt.utils.str2bool import str2bool


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Classes ###############
# ##################################


class JobPluginsDownloader(GenericJob):
    """
    Job to download plugins.
    """

    ID: str = "qplugins-downloader"
    OPTIONS_SCHEMA: dict = {
        "force": {
            "type": bool,
            "required": False,
            "default": False,
            "possible_values": None,
            "condition": None,
        },
        "threads": {
            "type": int,
            "required": False,
            "default": 5,
            "possible_values": (1, 2, 3, 4, 5),
            "condition": "in",
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

    def run(self) -> None:
        """Execute job logic."""
        # list plugins through different profiles
        qdt_referenced_plugins = self.list_referenced_plugins(
            parent_folder=self.qdt_downloaded_repositories
        )
        if qdt_referenced_plugins is None or not len(qdt_referenced_plugins):
            logger.info(
                f"No plugin found in profile.json files within {self.qdt_working_folder}"
            )
            return

        # filter plugins to download, filtering out those which are not already present locally
        if self.options.get("force") is True:
            qdt_plugins_to_download = qdt_referenced_plugins
            qdt_plugins_to_copy = []
        else:
            qdt_plugins_to_download = self.filter_list_downloadable_plugins(
                input_list=qdt_referenced_plugins
            )
            qdt_plugins_to_copy = self.filter_list_copiable_plugins(
                input_list=qdt_referenced_plugins
            )
            if not len(qdt_plugins_to_download + qdt_plugins_to_copy):
                logger.info(
                    f"All referenced plugins are already present in {self.qdt_plugins_folder}. "
                    "Skipping download/copy step."
                )
                return

        # launch download
        if len(qdt_plugins_to_download):
            downloaded_plugins, failed_downloads = self.download_remote_plugins(
                plugins_to_download=qdt_plugins_to_download,
                destination_parent_folder=self.qdt_plugins_folder,
                threads=self.options.get("threads", 5),
            )
            logger.debug(f"{len(downloaded_plugins)} plugins downloaded.")
            if len(failed_downloads):
                logger.error(
                    f"{len(failed_downloads)} failed plugin downloads. Check previous log lines."
                )

        if len(qdt_plugins_to_copy):
            copied_plugins, failed_copies = self.copy_plugins(
                plugins_to_copy=qdt_plugins_to_copy,
                destination_parent_folder=self.qdt_plugins_folder,
            )
            logger.debug(f"{len(copied_plugins)} plugins copied.")
            if len(failed_copies):
                logger.error(
                    f"{len(failed_copies)} failed plugin copies. Check previous log lines."
                )

        logger.debug(f"Job {self.ID} ran successfully.")

    def copy_plugins(
        self, plugins_to_copy: list[QgisPlugin], destination_parent_folder: Path
    ) -> tuple[list[QgisPlugin], list[QgisPlugin]]:
        """Copy listed plugins into the specified folder.

        Args:
            plugins_to_copy (List[QgisPlugin]): list of plugins to copy
            destination_parent_folder (Path): where to store copied plugins

        Returns:
            Tuple[List[QgisPlugin],List[QgisPlugin]]: tuple of (copied plugins, failed copies)
        """
        copied_plugins: list[QgisPlugin] = []
        failed_plugins: list[QgisPlugin] = []

        logger.debug(
            f"Copying {len(plugins_to_copy)} plugins into {destination_parent_folder}."
        )
        for plugin in plugins_to_copy:
            # check if source plugin can be accessed
            try:
                check_path(
                    input_path=plugin.url,
                    must_be_a_file=True,
                    must_be_readable=True,
                    must_be_a_folder=False,
                    must_exists=True,
                )
                src_plugin_path = Path(plugin.url)
            except Exception as err:
                logger.error(
                    f"The plugin '{plugin.name}' can't be copied from {plugin.url}. Trace: {err}."
                )
                failed_plugins.append(plugin)
                continue

            # try to copy
            try:
                dst_plugin_path = destination_parent_folder / src_plugin_path.name
                copy2(src=src_plugin_path, dst=destination_parent_folder)
                logger.info(
                    f"Plugin {plugin.name} has been copied from {src_plugin_path} "
                    f"to {dst_plugin_path}"
                )
                check_path(
                    input_path=dst_plugin_path,
                    must_be_a_file=True,
                    must_exists=True,
                    raise_error=True,
                )

                dst_plugin_path_final = dst_plugin_path.rename(
                    dst_plugin_path.with_name(f"{plugin.id_with_version}.zip")
                )
                logger.debug(
                    f"Plugin ZIP archive has been renamed from '{dst_plugin_path}' "
                    f"into '{dst_plugin_path_final}' to make it consistent with sync."
                )

                copied_plugins.append(plugin)
            except Exception as err:
                logger.error(
                    f"Copy of plugin {plugin.name} from {plugin.url} failed. Trace: {err}"
                )
                failed_plugins.append(plugin)
                continue

        return copied_plugins, failed_plugins

    def download_remote_plugins(
        self,
        plugins_to_download: list[QgisPlugin],
        destination_parent_folder: Path,
        threads: int = 5,
    ) -> tuple[list[QgisPlugin], list[QgisPlugin]]:
        """Download listed plugins into the specified folder, using multithreads or not.

        Args:
            plugins_to_download (List[QgisPlugin]): list of plugins to download
            destination_parent_folder (Path): where to store downloaded plugins
            threads (int, optional): number of threads to use. If 0, downloads will be \
                performed synchronously. Defaults to 5.

        Returns:
            Tuple[List[QgisPlugin],List[QgisPlugin]]: tuple of \
                (downloaded plugins, failed downloads)
        """
        downloaded_plugins: list[QgisPlugin] = []
        failed_plugins: list[QgisPlugin] = []

        if threads < 2:
            logger.debug(
                f"Downloading {len(plugins_to_download)} plugins in a single thread."
            )
            for plugin in plugins_to_download:
                # local path
                plugin_download_path = Path(
                    destination_parent_folder, f"{plugin.id_with_version}.zip"
                )
                try:
                    download_remote_file_to_local(
                        local_file_path=plugin_download_path,
                        remote_url_to_download=plugin.download_url,
                        content_type="application/zip, application/x-zip-compressed, application/octet-stream, multipart/x-zip",
                        use_stream=str2bool(getenv("QDT_STREAMED_DOWNLOADS", True)),
                    )
                    logger.info(
                        f"Plugin {plugin.name} from {plugin.download_url} "
                        f"downloaded in {plugin_download_path}"
                    )
                    downloaded_plugins.append(plugin)
                except Exception as err:
                    logger.error(
                        f"Download of plugin {plugin.name} failed. Trace: {err}"
                    )
                    failed_plugins.append(plugin)
                    continue
        else:
            logger.debug(
                f"Downloading {len(plugins_to_download)} plugins in {threads} threads."
            )
            with ThreadPoolExecutor(
                max_workers=threads, thread_name_prefix=f"{__title_clean__}"
            ) as executor:
                for plugin in plugins_to_download:
                    # local path
                    plugin_download_path = Path(
                        destination_parent_folder, f"{plugin.id_with_version}.zip"
                    )

                    # submit download to pool
                    try:
                        executor.submit(
                            # func to execute
                            download_remote_file_to_local,
                            # func parameters
                            local_file_path=plugin_download_path,
                            remote_url_to_download=plugin.download_url,
                            content_type="application/zip, application/x-zip-compressed, application/octet-stream, multipart/x-zip",
                            use_stream=str2bool(getenv("QDT_STREAMED_DOWNLOADS", True)),
                        )
                        downloaded_plugins.append(plugin)
                    except Exception as err:
                        logger.error(err)
                        failed_plugins.append(plugin)

        return downloaded_plugins, failed_plugins

    def list_referenced_plugins(self, parent_folder: Path) -> list[QgisPlugin] | None:
        """Return a list of plugins referenced in profile.json files found within a \
            parent folder and sorted by unique id with version.

        Args:
            parent_folder (Path): folder to start searching for profile.json files

        Returns:
            List[QgisPlugin]: list of plugins referenced within profile.json files
        """
        unique_plugins_identifiers: list = []
        all_profiles: list[QgisPlugin] = []

        # check of there are some profiles folders within the downloaded folder
        li_qdt_downloaded_profiles = self.list_downloaded_profiles()
        if li_qdt_downloaded_profiles is None:
            logger.error("No QGIS profile found in the downloaded folder.")
            return

        for qdt_profile in li_qdt_downloaded_profiles:
            for plugin in qdt_profile.plugins:
                if plugin.id_with_version not in unique_plugins_identifiers:
                    unique_plugins_identifiers.append(plugin.id_with_version)
                    all_profiles.append(plugin)

        logger.debug(
            f"{len(unique_plugins_identifiers)} unique plugins referenced in "
            f"{len(li_qdt_downloaded_profiles)} profiles in {parent_folder.resolve()}: "
            f"{','.join(sorted(unique_plugins_identifiers))}"
        )
        return sorted(all_profiles, key=lambda x: x.id_with_version)

    def filter_list_downloadable_plugins(
        self, input_list: list[QgisPlugin]
    ) -> list[QgisPlugin]:
        """Filter input list of plugins keeping only those are remotly stored and which
            are not present within the local QDT plugins folder.

        Args:
            input_list (List[QgisPlugin]): list of plugins to filter

        Returns:
            List[QgisPlugin]: list of plugins to download
        """
        plugins_to_download = []

        for plugin in input_list:
            # keep only if remote
            if plugin.location != "remote":
                logger.debug(
                    f"Ignoring plugin '{plugin.name}' because it's not stored remotly."
                )
                continue

            # build destination path
            plugin_download_path = Path(
                self.qdt_plugins_folder, f"{plugin.id_with_version}.zip"
            )

            # check if file already exists
            if plugin_download_path.is_file():
                logger.debug(
                    f"Plugin already exists at {plugin_download_path}, so it won't be downloaded."
                )
                continue

            plugins_to_download.append(plugin)

        return plugins_to_download

    def filter_list_copiable_plugins(
        self, input_list: list[QgisPlugin]
    ) -> list[QgisPlugin]:
        """Filter input list of plugins keeping only those which are stored locally and
            which are not present within the local QDT plugins folder.

        Args:
            input_list (List[QgisPlugin]): list of plugins to filter

        Returns:
            List[QgisPlugin]: list of plugins to copy from local disk or network
        """
        plugins_to_copy = []

        for plugin in input_list:
            # keep only if remote
            if plugin.location != "local":
                logger.debug(
                    f"Ignoring plugin '{plugin.name}' because it's not stored locally."
                )
                continue

            # build destination path
            plugin_destination_path = Path(
                self.qdt_plugins_folder, f"{plugin.id_with_version}.zip"
            )

            # check if file already exists
            if plugin_destination_path.is_file():
                logger.debug(
                    f"Plugin already exists at {plugin_destination_path}, so it "
                    "won't be copied from source."
                )
                continue

            plugins_to_copy.append(plugin)

        return plugins_to_copy


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    """Standalone execution."""
    pass
