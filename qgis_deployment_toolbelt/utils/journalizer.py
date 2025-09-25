#! python3  # noqa: E265

"""Helper to configure logging depending on CLI options."""

# ############################################################################
# ########## IMPORTS #############
# ################################

# standard library
import logging
from getpass import getuser
from logging.handlers import RotatingFileHandler
from os import environ, getenv
from pathlib import Path
from platform import architecture, platform, uname
from socket import gethostname

# 3rd party
import certifi
from requests.utils import DEFAULT_CA_BUNDLE_PATH


# Imports depending on operating system
if "linux" in uname().system.lower():
    import distro
else:
    distro = None

# package
from qgis_deployment_toolbelt.__about__ import __title__, __version__
from qgis_deployment_toolbelt.constants import get_qdt_logs_folder
from qgis_deployment_toolbelt.utils.proxies import get_proxy_settings
from qgis_deployment_toolbelt.utils.str2bool import str2bool


# ############################################################################
# ########## GLOBALS #############
# ################################

# logs
logger = logging.getLogger(__name__)

# ############################################################################
# ########## FUNCTIONS ###########
# ################################


def configure_logger(verbosity: int = 1, logfile: None | Path | str = None):
    """Configure logging according to verbosity from CLI.

    Args:
        verbosity (int): verbosity level
        logfile (Path, optional): file where to store log. Defaults to None.
    """
    # handle log level overridden by environment variable
    verbosity = getenv("QDT_LOGS_LEVEL", verbosity)
    try:
        verbosity = int(verbosity)
    except ValueError as err:
        logger.error(f"Bad verbosity value type: {err}. Fallback to 1.")
        verbosity = 1

    # set log level depending on verbosity argument
    if 0 < verbosity < 4:
        verbosity = 40 - (10 * verbosity)
    elif verbosity >= 4:
        # debug is the limit
        verbosity = 40 - (10 * 3)
    else:
        verbosity = 0

    # set console handler
    log_console_handler = logging.StreamHandler()
    log_console_handler.setLevel(verbosity)

    # set log file
    if not logfile:
        logging.basicConfig(
            level=verbosity,
            format="%(asctime)s||%(levelname)s||%(module)s||%(funcName)s||%(lineno)d||%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[log_console_handler],
        )

    else:
        logs_folder = get_qdt_logs_folder()

        # make sure folder exists
        logs_folder.mkdir(exist_ok=True, parents=True)
        logs_filepath = Path(logs_folder, logfile)

        log_file_handler = RotatingFileHandler(
            backupCount=10,
            delay=True,
            encoding="UTF-8",
            filename=logs_filepath,
            maxBytes=3000000,
            mode="a",
        )

        # force new file by execution
        if logs_filepath.is_file():
            log_file_handler.doRollover()

        logging.basicConfig(
            level=verbosity,
            format="%(asctime)s||%(levelname)s||%(module)s||%(funcName)s||%(lineno)d||%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            handlers=[log_console_handler, log_file_handler],
        )

        logger.info(f"Log file: {logs_filepath}")

    headers()


def headers():
    """Basic information to log before other message."""
    # initialize the log
    logger.info(f"{'=' * 10} {__title__} - {__version__} {'=' * 10}")
    logger.debug(f"Operating System: {platform()}")
    if distro:
        logger.debug(
            f"Distribution name and version: {distro.name()} {distro.version()}"
        )
    logger.debug(f"Architecture: {architecture()[0]}")
    logger.debug(f"Computer: {gethostname()}")
    logger.debug(f"Launched by user: {getuser()}")

    if getenv("userdomain"):
        logger.debug(f"OS Domain: {getenv('userdomain')}")
    else:
        logger.debug("No OS domain detected.")

    if proxies_settings := get_proxy_settings():
        logger.debug(f"Network proxies detected: {proxies_settings}")
    else:
        logger.debug("No network proxies detected")

    # SSL CA certificates
    logger.debug(f"Installed certificate authority (CA) bundle: {certifi.where()}")
    logger.debug(f"Default certificate authority (CA) bundle: {DEFAULT_CA_BUNDLE_PATH}")
    logger.debug(
        f"Certificate authority (CA) bundle to use: {getenv('REQUESTS_CA_BUNDLE', getenv('CURL_CA_BUNDLE'))}"
    )

    if str2bool(getenv("QDT_SSL_USE_SYSTEM_STORES", False)):
        logger.debug("Option to use native system certificates stores is enabled.")
        if "REQUESTS_CA_BUNDLE" in environ:
            environ.pop("REQUESTS_CA_BUNDLE")
            logger.debug(
                "Custom path to CA Bundle (REQUESTS_CA_BUNDLE) has been removed from "
                "environment variables."
            )
        if "CURL_CA_BUNDLE" in environ:
            environ.pop("CURL_CA_BUNDLE")
            logger.debug(
                "Custom path to CA Bundle (CURL_CA_BUNDLE) has been removed from "
                "environment variables."
            )


def get_logger_filepath() -> Path | None:
    """Retrieve log filepath within logger handlers.

    Returns:
        Path | None: path to the logfile or None if no handler has baseFilename attr.
    """
    if logger.root.hasHandlers():
        for handler in logger.root.handlers:
            if hasattr(handler, "baseFilename"):
                return Path(handler.baseFilename)

    logger.warning("No file found in any log handlers.")
    return None
