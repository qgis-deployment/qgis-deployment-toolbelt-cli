#! python3  # noqa: E265

"""
Helpers to check file: readable, exists, etc..

Author: Julien Moura (https://github.com/guts)
"""

# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from pathlib import PurePosixPath
from urllib.parse import urlparse, urlsplit

# package
from qgis_deployment_toolbelt.utils.slugger import sluggy


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)

# #############################################################################
# ########## Functions #############
# ##################################


def check_str_is_url(
    input_str: str,
    ref_shemes: tuple = ("http", "https"),
    raise_error: bool = True,
):
    """Checks if a given str is a valid URL.

    Args:
        input_str (str): The input str to check.
        ref_schemes (tuple, optional): The reference schemes for valid URLs.
            By default, it includes ("http", "https").
        raise_error (bool, optional): Indicates whether an exception should be raised
            for invalid str. Default is True.

    Returns:
        bool: True if the str is a valid URL, False otherwise.

    Raises:
        ValueError: If the str is not a valid URL and `raise_error` is True.
        TypeError: If an error occurs during str checking and `raise_error` is True.
    """
    # convert into str
    if not isinstance(input_str, str):
        logger.warning(
            f"{input_str} is not a str but {type(input_str)}. Take care, "
            "the conversion is not safe..."
        )
        input_str = str(input_str)

    try:
        parsed_url = urlparse(input_str)
        if parsed_url.scheme in ref_shemes and parsed_url.netloc:
            logger.debug(f"{input_str} is a valid URL.")
            return True
        else:
            error_message = f"{input_str} is not a valid URL."
            if raise_error:
                raise ValueError(error_message)
            logger.debug(error_message)
            return False
    except ValueError as err:
        error_message = f"{input_str} is not a valid URL. An error occurred during check. Trace : {err}"
        if raise_error:
            raise TypeError(error_message) from err
        logger.warning(error_message)
        return False


def filename_from_url(url: str) -> str:
    """Try to determine filename from a given download URL.

    Args:
        url (str): URL to remote file

    Returns:
        str: determined filename
    """
    url_splitted = urlsplit(url)

    url_host = sluggy(url_splitted.netloc)
    url_path = PurePosixPath(url_splitted.path)
    url_file_parent = url_path.parent
    url_file_name = url_path.name

    if url_file_parent in (PurePosixPath("/"), PurePosixPath("."), PurePosixPath("")):
        parent_slug = ""
    else:
        parent_slug = sluggy(str(url_file_parent).lstrip("/"))

    segments = [url_host]

    if parent_slug:
        segments.append(parent_slug)

    if url_file_name:
        segments.append(url_file_name)

    return "/".join(segments)
