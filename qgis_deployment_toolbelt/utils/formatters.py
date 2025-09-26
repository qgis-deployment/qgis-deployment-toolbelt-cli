#! python3  # noqa: E265

"""Helpers to format text and variables."""


# #############################################################################
# ########## Libraries #############
# ##################################

# Standard library
import logging
from functools import lru_cache
from math import floor, log as math_log


# #############################################################################
# ########## Globals ###############
# ##################################

# logs
logger = logging.getLogger(__name__)


# #############################################################################
# ########## Functions #############
# ##################################


@lru_cache
def convert_octets(octets: int) -> str:
    """Convert a mount of octets in readable size.

    Args:
        octets: mount of octets to convert

    Returns:
        size in a human readable format: ko, Mo, etc.

    Example:

    .. code-block:: python

        >>> convert_octets(1024)
        1 ko
        >>> from pathlib import Path
        >>> convert_octets(Path(my_file.txt).stat().st_size)
    """
    # check zero
    if octets == 0:
        return "0 octet"

    # conversion
    size_name = ("octets", "Ko", "Mo", "Go", "To", "Po")
    i = int(floor(math_log(octets, 1024)))
    p = pow(1024, i)
    s = round(octets / p, 2)

    return f"{s} {size_name[i]}"


@lru_cache
def url_ensure_trailing_slash(in_url: str) -> str:
    """Make sure an URL has a trailing slash.

    Args:
        in_url (str): input URL

    Returns:
        str: URL with trailing slash added (only if not already present)
    """
    if in_url.endswith("/"):
        logger.debug(f"URL already had a trailing slash: {in_url}")
        return in_url
    else:
        logger.debug(f"A trailing slash has been added to input URL: {in_url}/")
        return f"{in_url}/"
