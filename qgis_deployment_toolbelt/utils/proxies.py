#! python3  # noqa: E265

"""
Small module to get network proxies configuration.

Author: Julien Moura (github.com/guts)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
import os
from collections.abc import Callable
from functools import lru_cache
from os import environ
from pathlib import Path
from urllib.request import getproxies

# 3rd party
from pypac import get_pac, pac_context_for_url
from pypac.parser import PACFile

# package
from qgis_deployment_toolbelt.utils.url_helpers import check_str_is_url


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Functions #############
# ##################################
@lru_cache
def get_proxy_settings(url: str | None = None) -> dict:
    """Retrieves network proxy settings from operating system configuration or
    environment variables.
    Args:
        url (str, optional): url for request in case of PAC file use
    Returns:
        dict: proxy settings with protocl as key and URL as value
    """

    proxy_settings = {}
    if environ.get("QDT_PROXY_HTTP"):
        proxy_settings = {
            "http": environ.get("QDT_PROXY_HTTP"),
            "https": environ.get("QDT_PROXY_HTTP"),
        }
        logger.info(
            "Proxies settings from custom QDT in environment vars (QDT_PROXY_HTTP): "
            f"{proxy_settings}"
        )
    elif qdt_pac_file := environ.get("QDT_PAC_FILE"):
        if pac := load_pac_file_from_environment_variable(qdt_pac_file=qdt_pac_file):
            proxy_settings = get_proxy_settings_from_pac_file(url=url, pac=pac)
            logger.info(
                f"Proxies settings from environment vars PAC file: {environ.get('QDT_PAC_FILE')}"
                f"{proxy_settings}"
            )
        else:
            logger.warning(
                f"Invalid PAC file from environment vars PAC file : {environ.get('QDT_PAC_FILE')}. No proxy use."
            )
    elif pac := get_pac():
        proxy_settings = get_proxy_settings_from_pac_file(url=url, pac=pac)
        logger.info(f"Proxies settings from system PAC file: {proxy_settings}")
    elif getproxies():
        proxy_settings = getproxies()
        logger.debug(f"Proxies settings found in the OS: {proxy_settings}")
    elif environ.get("HTTP_PROXY") or environ.get("HTTPS_PROXY"):
        if environ.get("HTTP_PROXY") and environ.get("HTTPS_PROXY"):
            proxy_settings = {
                "http": environ.get("HTTP_PROXY"),
                "https": environ.get("HTTPS_PROXY"),
            }
            logger.info(
                "Proxies settings from generic environment vars (HTTP_PROXY "
                f"and HTTPS_PROXY): {proxy_settings}"
            )
        elif environ.get("HTTP_PROXY") and not environ.get("HTTPS_PROXY"):
            proxy_settings = {
                "http": environ.get("HTTP_PROXY"),
            }
            logger.info(
                "Proxies settings from generic environment vars (HTTP_PROXY only): "
                f"{proxy_settings}"
            )
        elif not environ.get("HTTP_PROXY") and environ.get("HTTPS_PROXY"):
            proxy_settings = {
                "https": environ.get("HTTPS_PROXY"),
            }
            logger.info(
                "Proxies settings from generic environment vars (HTTPS_PROXY only): "
                f"{proxy_settings}"
            )
    else:
        logger.debug(
            "No proxy settings found in environment vars nor OS settings nor PAC File."
        )

    # check scheme and URL validity
    if isinstance(proxy_settings, dict):
        for scheme, proxy_url in proxy_settings.items():
            if not check_str_is_url(input_str=proxy_url, raise_error=False):
                logger.warning(
                    f"Proxy value for {scheme} is not a valid URL: {proxy_url}. Can "
                    "lead to troubles."
                )

    return proxy_settings


def load_pac_file_from_environment_variable(qdt_pac_file: str) -> PACFile | None:
    """Load PAC file with PyPAC from a environment variable

    Args:
        qdt_pac_file (str): path to PAC file

    Returns:
        Optional[PACFile]: loaded PAC file, None if value is invalid
    """
    if qdt_pac_file.startswith(("http",)):
        return get_pac(
            qdt_pac_file,
            allowed_content_types=[
                "text/plain",
                "application/x-ns-proxy-autoconfig",
                "application/x-javascript-config",
            ],
        )
    else:
        with Path(qdt_pac_file).open(encoding="UTF-8") as f:
            return PACFile(f.read())


def get_proxy_settings_from_pac_file(
    pac: PACFile, url: str | None = None
) -> dict[str, str]:
    """Define proxy settings from pac file

    Args:
        url (str): url for request in case of PAC file use
        pac (PACFile): _description_

    Returns:
        dict[str, str]: _description_
    """

    proxy_settings = {}
    with pac_context_for_url(url=url, pac=pac):
        if environ.get("HTTP_PROXY"):
            proxy_settings["http"] = environ.get("HTTP_PROXY")
        if environ.get("HTTPS_PROXY"):
            proxy_settings["https"] = environ.get("HTTPS_PROXY")
    return proxy_settings


def os_env_proxy(func: Callable) -> Callable:
    def wrapper(*args: object, **kwargs: object) -> object:
        """Decorator wrapper to define environment variable for proxy use.

        If a proxy settings is available for https or http we:
        - backup current environment value
        - define environment value with proxy settings
        - run function
        - restore environment value if available


        Returns:
            function result
        """
        # Get proxy settings
        proxy_settings = get_proxy_settings()

        # Update environment variable and keep current value
        prev_http_proxy = None
        if "http" in proxy_settings:
            prev_http_proxy = environ.get("HTTP_PROXY")
            os.environ["HTTP_PROXY"] = proxy_settings["http"]
        prev_https_proxy = None
        if "https" in proxy_settings:
            prev_https_proxy = environ.get("HTTPS_PROXY")
            os.environ["HTTPS_PROXY"] = proxy_settings["https"]

        # Run function
        result = func(*args, **kwargs)

        # Restore environment variable if available or remove it
        if prev_http_proxy:
            os.environ["HTTP_PROXY"] = prev_http_proxy
        elif "HTTP_PROXY" in os.environ:
            del os.environ["HTTP_PROXY"]
        if prev_https_proxy:
            os.environ["HTTPS_PROXY"] = prev_https_proxy
        elif "HTTPS_PROXY" in os.environ:
            del os.environ["HTTPS_PROXY"]
        return result

    return wrapper


# #############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == "__main__":
    """Standalone execution."""
    pass
