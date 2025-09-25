#! python3  # noqa: E265

"""
Handle remote HTTP repository.

Author: Julien Moura (https://github.com/guts).
"""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from concurrent.futures import ThreadPoolExecutor
from os import getenv
from pathlib import Path
from shutil import rmtree

# 3rd party
import requests

# project
from qgis_deployment_toolbelt.__about__ import __title_clean__, __version__
from qgis_deployment_toolbelt.profiles.profiles_handler_base import (
    RemoteProfilesHandlerBase,
)
from qgis_deployment_toolbelt.utils.file_downloader import download_remote_file_to_local
from qgis_deployment_toolbelt.utils.formatters import url_ensure_trailing_slash
from qgis_deployment_toolbelt.utils.proxies import get_proxy_settings
from qgis_deployment_toolbelt.utils.str2bool import str2bool
from qgis_deployment_toolbelt.utils.tree_files_reader import tree_to_download_list


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)

# #############################################################################
# ########## Classes ###############
# ##################################


class HttpHandler(RemoteProfilesHandlerBase):
    """Handle remote HTTP repositories without git protocol.

    It's designed to handle thoses cases:

    - the distant repository (source) is on a webserver accessible through HTTP protocol
    - the local repository (destination) is on a local network or drive
    """

    # headers
    HTTP_HEADERS = {
        "User-Agent": f"{__title_clean__}/{__version__}",
    }

    def __init__(
        self,
        source_repository_path_or_uri: str,
        source_repository_type: str = "http",
    ) -> None:
        """Constructor.

        Args:
            source_repository_path_or_uri (str | Path): path to the source repository
        """
        self.SOURCE_REPOSITORY_PATH_OR_URL = url_ensure_trailing_slash(
            source_repository_path_or_uri
        )
        super().__init__(source_repository_type=source_repository_type)

    def download(self, destination_local_path: Path):
        """Generic wrapper around the specific logic of this handler.

        Args:
            destination_local_path (Path): path to the local folder where to download

        """
        logger.info(
            f"Start downloading from {self.SOURCE_REPOSITORY_PATH_OR_URL} to "
            f"{destination_local_path}"
        )

        try:
            logger.debug("Retrieve qdt-files.json ")
            # get qdt-files.json
            req = requests.get(
                url=f"{self.SOURCE_REPOSITORY_PATH_OR_URL}qdt-files.json",
                headers=self.HTTP_HEADERS,
                proxies=get_proxy_settings(
                    url=f"{self.SOURCE_REPOSITORY_PATH_OR_URL}qdt-files.json"
                ),
                timeout=(30, 60),
            )
            req.raise_for_status()
            qdt_tree = req.json()
        except Exception as err:
            logger.critical(
                f"Downloading {self.SOURCE_REPOSITORY_PATH_OR_URL} to "
                f"{destination_local_path} failed. Trace: {err}"
            )
            raise err

        # clean everything before downloading
        rmtree(path=destination_local_path, ignore_errors=True)

        # make sure destination path exists
        if not destination_local_path.exists():
            logger.debug(
                f"Destination folder ({destination_local_path}) does not exist. Let's create it!"
            )
            destination_local_path.mkdir(parents=True)

        li_files_to_download = tree_to_download_list(tree_array=qdt_tree)
        logger.info(f"{len(li_files_to_download)} files to download")

        success, fails = self.download_files_to_local(
            li_files_to_download=li_files_to_download,
            target_folder=destination_local_path,
        )
        if not len(success):
            logger.error("No files downloaded! Please check the above log messages.")
        if len(fails):
            logger.warning(
                f"{len(fails)} download failed. Check the above log messages."
            )

    def download_files_to_local(
        self, li_files_to_download: list[str], target_folder: Path
    ) -> tuple[list[tuple[str, Path]], list[tuple[str, str]]]:
        """Download list of files relative to remote base URL to local target folder.

        Args:
            li_files_to_download (list[str]): list of files to download.
            target_folder (Path): local folder where to download

        Returns:
            (list of success download, list of failed download)
        """
        base_url = self.SOURCE_REPOSITORY_PATH_OR_URL
        downloaded_files: list[tuple[str, Path]] = []
        failed_files: list[tuple[str, str]] = []

        with ThreadPoolExecutor(
            thread_name_prefix=f"{__title_clean__}_profile_dl_http_"
        ) as executor:
            for file_to_download in li_files_to_download:
                # submit download to pool
                try:
                    executor.submit(
                        # func to execute
                        download_remote_file_to_local,
                        # func parameters
                        local_file_path=target_folder.joinpath(file_to_download),
                        remote_url_to_download=f"{base_url}{file_to_download}",
                        use_stream=str2bool(getenv("QDT_STREAMED_DOWNLOADS", True)),
                    )
                    downloaded_files.append(
                        (
                            f"{base_url}{file_to_download}",
                            target_folder.joinpath(file_to_download),
                        )
                    )
                except Exception as err:
                    failed_files.append((file_to_download, f"{err}"))

        return downloaded_files, failed_files
