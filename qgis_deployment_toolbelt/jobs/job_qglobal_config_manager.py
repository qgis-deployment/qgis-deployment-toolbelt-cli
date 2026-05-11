#! python3  # noqa: E265

"""Job handling QGIS global settings INI file manipulation."""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from os import getenv
from pathlib import Path
from posixpath import expanduser, expandvars

# package
from qgis_deployment_toolbelt.constants import OSConfiguration
from qgis_deployment_toolbelt.jobs.generic_job import GenericJob
from qgis_deployment_toolbelt.utils.file_downloader import download_remote_file_to_local
from qgis_deployment_toolbelt.utils.str2bool import str2bool
from qgis_deployment_toolbelt.utils.url_helpers import (
    check_str_is_url,
    filename_from_url,
)


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)

# #############################################################################
# ########## Classes ###############
# ##################################


class JobQgisGlobalConfigManager(GenericJob):
    """
    Class to manage the global config of QGIS installation.
    """

    ID: str = "qglobal-config-manager"
    OPTIONS_SCHEMA: dict = {
        "src": {
            "type": str,
            "required": True,
            "possible_values": None,
            # from QDT working directory or local scenario folder
            "default": "./global/qgis_global_settings.ini",
        },
        "dst": {
            "type": str,
            "required": False,
            "default": None,
            "possible_values": None,
        },
    }

    def __init__(self, options: dict) -> None:
        """Instantiate the class.
        Args:
            options (dict): dictionnary with job options or remove.
        """

        super().__init__()
        self.options: dict = self.validate_options(options)

    def run(self) -> None:
        """Copy QGIS global settings file to a custom destination and update
        environment variable for file use in QGIS."""

        # Define source file
        src_path = self.get_src_ini_file(self.options.get("src", None))

        # # Get destination file
        # dst_path = self.get_dst_ini_file(self.options.get("dst", None))

        # # Copy source to destination
        # try:
        #     logger.info(f"Copying `{src_path}` to `{dst_path}`")

        #     # Create directory for destination
        #     dst_path.parent.mkdir(parents=True, exist_ok=True)

        #     # Copy current installed file
        #     copy2(
        #         src_path,
        #         dst_path,
        #     )

        #     dst_ini_helper = QgisIniHelper(
        #         ini_filepath=dst_path, ini_type="qgis_global_settings"
        #     )
        #     src_ini_helper = QgisIniHelper(
        #         ini_filepath=src_path, ini_type="qgis_global_settings"
        #     )

        #     # Merge
        #     logger.info(
        #         f"Environment variable conversion from `{src_path}` to `{dst_path}`"
        #     )
        #     src_ini_helper.merge_to(dst_ini_helper)

        # except Exception as exc:
        #     err_msg = (
        #         f"Can't copy `{src_path}` to `{dst_path}` for job {self.ID}. "
        #         f"Check permission for destination. Trace: {exc}"
        #     )
        #     raise ValueError(err_msg) from exc

        # # Update environment variable
        # if set_environment_variable is not None:
        #     logger.info(
        #         f"QGIS_GLOBAL_SETTINGS_FILE environment variable set to `{dst_path}`"
        #     )
        #     set_environment_variable(
        #         envvar_name="QGIS_GLOBAL_SETTINGS_FILE",
        #         envvar_value=str(dst_path),
        #     )

        logger.debug(f"Job {self.ID} ran successfully.")

    def get_src_ini_file(self, src: str | None) -> Path:
        """Get source .ini file from job option.

        Args:
            src (str | None): `src` job option

        Raises:
            ValueError: Can't define default option for None input
            ValueError: Can't download .ini file for input url
            ValueError: `src` option use a file not available

        Returns:
            Path: path to source .ini file
        """
        logger.info(f"Source file passed as parameter (raw): {src}")

        # Interpolate value
        src = expandvars(expanduser(src))
        logger.info(f"Source file (expanded): {src}")

        # Check if src is a url
        if check_str_is_url(input_str=src, raise_error=False):
            logger.info(
                f"Remote global config file '{src}' is a valid URL. Downloading QGIS global settings file..."
            )
            try:
                src = self.get_remote_qgis_global_settings_from_url(remote_url=src)
            except Exception as exc:
                err_msg = (
                    f"Error download external url `{src}` for job {self.ID}. "
                    f"Trace: {exc}. Can't update QGIS global settings file."
                )
                raise ValueError(err_msg) from exc

        src_path = Path(src)

        # Check if file is relative
        if not src_path.is_absolute():
            local_file_match: bool = False

            logger.info(
                f"{src} is a relative path. Starting conversion into absolute path."
            )

            # Check with downloaded repositories in current scenario
            logger.info(
                f"Check if it's relative to the downloaded repository of current scenario: "
                f"{self.qdt_current_scenario} or then if it's relative to the "
                f"working directory: {self.qdt_working_folder}"
            )
            if Path(self.qdt_current_scenario / src_path).exists():
                src_path = Path(self.qdt_current_scenario / src_path).resolve()
                local_file_match = True
                logger.info(f"Matching repository of current scenario: {src}.")
            else:
                logger.info(
                    f"No match with current scenario repository, "
                    f"{Path(self.qdt_current_scenario / src_path)} does not exits. "
                    "Checking with QDT working directory."
                )

            # Check with QDT working dir
            if (
                not local_file_match
                and Path(self.qdt_working_folder / src_path).exists()
            ):
                src_path = Path(self.qdt_working_folder / src_path).resolve()
                logger.info(f"Matching QDT working folder of current scenario: {src}.")
            else:
                logger.info(
                    f"No match with local QDT working folder, "
                    f"{Path(self.qdt_working_folder / src_path)} does not exits. "
                    "Fallback to current folder."
                )

            if not local_file_match:
                src_path = src_path.resolve()
                logger.warning(
                    f"{src} relative path converted from current directory: {src_path}"
                )

        # Check file exists
        if src_path is None or not src_path.exists():
            err_msg = (
                f"src option file `{src}` is not available for job {self.ID}. "
                "Can't update QGIS global settings file."
            )
            raise ValueError(err_msg)

        return src_path

    def get_dst_ini_file(self, dst: str | None) -> Path:
        """Get destination .ini file from job option

        Args:
            dst (str | None): `dst` job option

        Raises:
            ValueError: `dst` option uses a relative file
            ValueError: Can't define destination .ini file from default option

        Returns:
            Path: path to destination .ini file
        """

        if dst is None:
            os_config: OSConfiguration = OSConfiguration.from_opersys()
            dst = os_config.get_qgis_global_settings_file_path(check_exists=False)

        # Interpolate value
        dst = expandvars(expanduser(dst))

        dst_path = Path(dst)

        if not dst_path.is_absolute():
            err_msg = (
                f"dst option file path `{dst_path}` must be absolute "
                f"for job {self.ID}. Can't update QGIS global settings file."
            )
            raise ValueError(err_msg)

        if dst_path is None:
            err_msg = f"Can't define destination for job {self.ID}."
            raise ValueError(err_msg)
        return dst_path

    def get_remote_qgis_global_settings_from_url(self, remote_url: str) -> Path:
        """Download remote qgis global settings and return local file path.

        Args:
            remote_url (str): URL to remote qgis global settings

        Returns:
            Path: local path to downloaded qgis global settings.
        """
        # try to build file path from URL
        try:
            local_filepath_for_remote_global_settings = (
                f"remote_qgis_global_settings/{filename_from_url(remote_url)}"
            )
        except Exception as err:
            local_filepath_for_remote_global_settings = (
                "remote_qgis_global_settings/qgis_global_settings.ini"
            )
            logger.warning(
                f"Failed to extract a proper filename from URL: {remote_url}. "
                f"Trace: {err}. "
                f"Fallback to default: {local_filepath_for_remote_global_settings}"
            )

        return download_remote_file_to_local(
            remote_url_to_download=remote_url,
            local_file_path=Path(
                self.qdt_working_folder.parent,
                local_filepath_for_remote_global_settings,
            ),
            use_stream=str2bool(getenv("QDT_STREAMED_DOWNLOADS", True)),
        )
