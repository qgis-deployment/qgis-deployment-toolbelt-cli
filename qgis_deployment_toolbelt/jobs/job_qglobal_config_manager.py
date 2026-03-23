#! python3  # noqa: E265

"""
Tools to manage the environment setup (variables, etc.)

Author: Julien Moura (https://github.com/guts)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from os import getenv
from pathlib import Path
from shutil import copy2
from sys import platform as opersys
from urllib.parse import urlsplit

# package
from qgis_deployment_toolbelt.constants import OSConfiguration
from qgis_deployment_toolbelt.jobs.generic_job import GenericJob
from qgis_deployment_toolbelt.profiles.qgis_ini_handler import QgisIniHelper
from qgis_deployment_toolbelt.utils.file_downloader import download_remote_file_to_local
from qgis_deployment_toolbelt.utils.slugger import sluggy
from qgis_deployment_toolbelt.utils.str2bool import str2bool
from qgis_deployment_toolbelt.utils.url_helpers import check_str_is_url


# 3rd party
# conditional imports
if opersys == "win32":
    from qgis_deployment_toolbelt.utils.win32utils import set_environment_variable
elif opersys == "linux":
    from qgis_deployment_toolbelt.utils.linux_utils import set_environment_variable
else:
    set_environment_variable = None

# #############################################################################
# ########## Globals ###############
# ##################################


# logs
logger = logging.getLogger(__name__)

# #############################################################################
# ########## Classes ###############
# ##################################


class JobGlobalConfigManager(GenericJob):
    """
    Class to manage the global config of QGIS installation.
    """

    ID: str = "qglobal-config-manager"
    OPTIONS_SCHEMA: dict = {
        "src": {
            "type": str,
            "required": True,
            "possible_values": None,
            "default": None,
        },
        "dst": {
            "type": str,
            "required": True,
            "default": None,
            "possible_values": None,
            "condition": None,
        },
    }

    def __init__(self, options: dict) -> None:
        """Instantiate the class.
        Args:
            options (dict): dictionnary with job options
            or remove.
        """

        super().__init__()
        self.options: dict = self.validate_options(options)

    def run(self) -> None:
        """Copy QGIS global settings file to a custom destination and update environment variable for file use in QGIS."""
        src = self.options.get("src", None)

        os_config: OSConfiguration = OSConfiguration.from_opersys()

        # Define source file

        if src is None:
            # Define default src file from os config
            src = os_config.get_qgis_global_settings_file_path(check_exists=True)

            if src is None:
                err_msg = f"Can't define default src option for job {self.ID}. Can't update QGIS global settings file."
                raise ValueError(err_msg)

        # Check if src is a url
        if check_str_is_url(input_str=src, raise_error=False):
            logger.info(f"{src} is a valid URL. Downloading QGIS global settings file.")
            try:
                src = self.get_remote_qgis_global_settings_from_url(remote_url=src)
            except Exception as exc:
                err_msg = f"Error download external url `{src}` for job {self.ID} : {exc}. Can't update QGIS global settings file."
                raise ValueError(err_msg) from exc

        src_path = Path(src)

        # Check if file is relative
        if not src_path.is_absolute():
            # Check with downloaded repositories
            if Path(self.qdt_downloaded_repositories / src_path).exists():
                src_path = Path(self.qdt_downloaded_repositories / src_path).resolve()
            # Check with QDT working dir
            elif Path(self.qdt_working_folder / src_path).exists():
                src_path = Path(self.qdt_working_folder / src_path).resolve()

        # Check file exists
        if not src_path.exists():
            err_msg = f"src option file `{src}` is not available for job {self.ID}. Can't update QGIS global settings file."
            raise ValueError(err_msg)

        # Get destination file
        dst = self.options.get("dst", None)
        if dst is None:
            dst_path = os_config.get_qgis_global_settings_file_path(check_exists=False)
        else:
            dst_path = Path(dst)

        if not dst_path.is_absolute():
            err_msg = f"dst option file path `{dst_path}` must be absolute for job {self.ID}. Can't update QGIS global settings file."
            raise ValueError(err_msg)

        if dst_path is None:
            err_msg = f"Can't define destination for job {self.ID}."
            raise ValueError(err_msg)

        # Copy source to destination
        try:
            # Create directory for destination
            dst_path.parent.mkdir(parents=True, exist_ok=True)

            # Copy current installed file
            copy2(
                src_path,
                dst_path,
            )

            dst_ini_helper = QgisIniHelper(
                ini_filepath=dst_path, ini_type="qgis_global_settings"
            )
            src_ini_helper = QgisIniHelper(
                ini_filepath=src_path, ini_type="qgis_global_settings"
            )

            # Merge
            src_ini_helper.merge_to(dst_ini_helper)

        except Exception:
            err_msg = f"Can't copy `{src_path}` to `{dst_path}` for job {self.ID}. Check permission for destination."
            raise ValueError(err_msg)

        # Update environment variable
        if set_environment_variable is not None:
            set_environment_variable(
                envvar_name="QGIS_GLOBAL_SETTINGS_FILE",
                envvar_value=str(dst_path),
            )

        logger.debug(f"Job {self.ID} ran successfully.")

    def get_remote_qgis_global_settings_from_url(self, remote_url: str) -> Path:
        """Download remote qgis global settings and return local file path.

        Args:
            remote_url (str): URL to remote qgis global settings

        Returns:
            Path: local path to downloaded qgis global settings.
        """
        # try to build file path from URL
        try:
            url_splitted = urlsplit(remote_url)
            local_filepath_for_remote_global_settings = (
                "remote_qgis_global_settings/"
                f"{sluggy(url_splitted.netloc)}/"
                f"{sluggy(str(Path(url_splitted.path).parent))}/"
                f"{Path(url_splitted.path).name}"
            )
        except Exception as err:
            local_filepath_for_remote_global_settings = (
                "remote_qgis_global_settings/qgis_global_settings.ini"
            )
            logger.warning(
                f"Failed to extract a proper filename from URL: {remote_url}."
                f" Trace: {err}. Fallback to default: {local_filepath_for_remote_global_settings}"
            )

        return download_remote_file_to_local(
            remote_url_to_download=remote_url,
            local_file_path=Path(
                self.qdt_working_folder.parent,
                local_filepath_for_remote_global_settings,
            ),
            use_stream=str2bool(getenv("QDT_STREAMED_DOWNLOADS", True)),
        )
